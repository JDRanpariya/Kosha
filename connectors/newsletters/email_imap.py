"""
Email / Newsletter connector via IMAP.

Connects to an IMAP mailbox, fetches unread (or recent) emails,
parses HTML/plain-text bodies into Markdown, and returns ConnectorOutput objects.

Typical use cases
-----------------
- Newsletter emails (Substack, Morning Brew, TLDR, etc.) delivered to inbox
- Mailing list digests (Python-Dev, Hacker News digest, etc.)
- Any structured email you want searchable

Setup guide
-----------
Gmail:
  1. Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP
  2. Google Account → Security → 2-Step Verification → App Passwords
  3. Use imap.gmail.com : 993

Fastmail:   imap.fastmail.com : 993
Outlook:    outlook.office365.com : 993

Security note
-------------
Store the password in infra/secrets/email_password.txt and load it via
settings.EMAIL_PASSWORD — never hardcode it in config_json.
"""

import email
import imaplib
import logging
from datetime import datetime, timezone
from email.header import decode_header as _decode_header
from email.utils import parsedate_to_datetime
from typing import Optional

from markdownify import markdownify as md

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)


class EmailImapConfig(ConnectorConfig):
    imap_host: str                    # e.g. "imap.gmail.com"
    username: str                     # full email address
    password: str                     # app password or IMAP password
    imap_port: int = 993              # SSL port (standard)
    mailbox: str = "INBOX"            # mailbox / label to read from
    sender_filter: str = ""          # partial match on From: e.g. "@substack.com"
    subject_filter: str = ""         # partial match on Subject:
    max_results: int = 20             # max emails to fetch per run
    mark_as_read: bool = False        # mark fetched emails as \\Seen
    only_unread: bool = True          # restrict search to UNSEEN emails


class EmailImapConnector(BaseConnector):
    """
    Fetches newsletter / mailing-list emails from an IMAP server.

    Example configs
    ---------------
    All unread emails from Substack senders (Gmail):
        {
            "imap_host": "imap.gmail.com",
            "username": "you@gmail.com",
            "password": "app-specific-password",
            "sender_filter": "@substack.com",
            "max_results": 20,
            "mark_as_read": true
        }

    A dedicated "Newsletters" label, 50 most recent regardless of read status:
        {
            "imap_host": "imap.gmail.com",
            "username": "you@gmail.com",
            "password": "app-specific-password",
            "mailbox": "Newsletters",
            "only_unread": false,
            "max_results": 50
        }
    """

    ConfigModel = EmailImapConfig
    source_type = "email_imap"

    # ── IMAP helpers ──────────────────────────────────────────────────────────

    def _connect(self) -> imaplib.IMAP4_SSL:
        self.logger.info(
            f"Connecting to {self.config.imap_host}:{self.config.imap_port} "
            f"as {self.config.username}"
        )
        conn = imaplib.IMAP4_SSL(self.config.imap_host, self.config.imap_port)
        conn.login(self.config.username, self.config.password)
        return conn

    def _build_search_criteria(self) -> str:
        """
        Build an IMAP SEARCH criteria string from config.

        IMAP search syntax reference:
          https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4
        """
        parts: list[str] = []

        if self.config.only_unread:
            parts.append("UNSEEN")
        if self.config.sender_filter:
            # IMAP FROM search is a substring match
            parts.append(f'FROM "{self.config.sender_filter}"')
        if self.config.subject_filter:
            parts.append(f'SUBJECT "{self.config.subject_filter}"')

        # IMAP requires criteria to be joined without AND keyword
        return " ".join(parts) if parts else "ALL"

    # ── parsing helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _decode_str(raw: str | None) -> str:
        """Decode RFC 2047 encoded header values (=?utf-8?b?...?=)."""
        if not raw:
            return ""
        parts = _decode_header(raw)
        result: list[str] = []
        for chunk, charset in parts:
            if isinstance(chunk, bytes):
                result.append(chunk.decode(charset or "utf-8", errors="replace"))
            else:
                result.append(str(chunk))
        return "".join(result).strip()

    @staticmethod
    def _extract_body(msg: email.message.Message) -> tuple[str, str]:
        """
        Walk a (possibly multipart) email and return (html_body, plain_body).
        Attachments are ignored.
        """
        html_body = ""
        plain_body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in disposition:
                    continue

                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                decoded = payload.decode(charset, errors="replace")

                if content_type == "text/html" and not html_body:
                    html_body = decoded
                elif content_type == "text/plain" and not plain_body:
                    plain_body = decoded
        else:
            charset = msg.get_content_charset() or "utf-8"
            payload = msg.get_payload(decode=True)
            if payload:
                decoded = payload.decode(charset, errors="replace")
                if msg.get_content_type() == "text/html":
                    html_body = decoded
                else:
                    plain_body = decoded

        return html_body, plain_body

    def _parse_message(self, raw_email: bytes) -> Optional[ConnectorOutput]:
        """Convert raw RFC 822 bytes into a ConnectorOutput."""
        try:
            msg = email.message_from_bytes(raw_email)
        except Exception as exc:
            self.logger.warning(f"Could not parse email bytes: {exc}")
            return None

        subject = self._decode_str(msg.get("Subject"))
        sender  = self._decode_str(msg.get("From"))
        msg_id  = (msg.get("Message-ID") or "").strip()

        # Use Message-ID as the canonical dedup URL.
        # email:// scheme keeps content_hash unique without a real HTTP URL.
        url = f"email://{msg_id}" if msg_id else f"email://no-id/{subject}"

        # Parse date
        published_at: datetime | None = None
        date_header = msg.get("Date", "")
        if date_header:
            try:
                published_at = (
                    parsedate_to_datetime(date_header)
                    .astimezone(timezone.utc)
                    .replace(tzinfo=None)
                )
            except Exception:
                pass

        html_body, plain_body = self._extract_body(msg)

        if html_body:
            content = md(html_body, heading_style="ATX").strip()
        elif plain_body:
            content = plain_body.strip()
        else:
            content = ""

        # Drop completely empty emails
        if not content and not subject:
            return None

        return ConnectorOutput(
            title=subject or "(no subject)",
            url=url,
            author=sender or None,
            published_at=published_at,
            content=content,
            metadata={
                "source_type": "newsletter",
                "platform": "email_imap",
                "message_id": msg_id,
                "from": sender,
                "mailbox": self.config.mailbox,
                "imap_host": self.config.imap_host,
            },
        )

    # ── main entry point ──────────────────────────────────────────────────────

    def fetch(self) -> list[ConnectorOutput]:
        try:
            conn = self._connect()
        except imaplib.IMAP4.error as exc:
            self.logger.error(f"IMAP login failed: {exc}")
            return []

        try:
            status, _ = conn.select(f'"{self.config.mailbox}"')
            if status != "OK":
                self.logger.error(f"Could not select mailbox {self.config.mailbox!r}")
                return []

            criteria = self._build_search_criteria()
            self.logger.info(
                f"Searching {self.config.mailbox!r} with criteria: {criteria!r}"
            )

            status, data = conn.search(None, criteria)
            if status != "OK" or not data or not data[0]:
                self.logger.warning("IMAP SEARCH returned no results")
                return []

            mail_ids: list[bytes] = data[0].split()

            # Take the N most recent (IMAP returns oldest-first)
            mail_ids = mail_ids[-self.config.max_results:][::-1]

            self.logger.info(f"Found {len(mail_ids)} matching emails to fetch")

            items: list[ConnectorOutput] = []

            for mail_id in mail_ids:
                status, msg_data = conn.fetch(mail_id, "(RFC822)")
                if status != "OK" or not msg_data or msg_data[0] is None:
                    continue

                raw_bytes = msg_data[0][1]
                if not isinstance(raw_bytes, bytes):
                    continue

                parsed = self._parse_message(raw_bytes)
                if parsed:
                    items.append(parsed)

                if self.config.mark_as_read:
                    conn.store(mail_id, "+FLAGS", "\\Seen")

            self.logger.info(
                f"Email connector: fetched {len(items)} items from {self.config.mailbox!r}"
            )
            return items

        finally:
            try:
                conn.logout()
            except Exception:
                pass
