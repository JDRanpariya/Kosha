import feedparser
from datetime import datetime
from time import mktime
from markdownify import markdownify as md
import logging

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)


class RssConfig(ConnectorConfig):
    feed_url: str
    max_results: int = 50


class RssNewsletterConnector(BaseConnector):
    ConfigModel = RssConfig
    source_type = "rss"

    def fetch(self) -> list[ConnectorOutput]:
        self.logger.info(f"Fetching RSS feed: {self.config.feed_url}")

        feed = feedparser.parse(self.config.feed_url)

        if feed.bozo and not feed.entries:
            self.logger.error(
                f"Failed to parse feed {self.config.feed_url}: {feed.bozo_exception}"
            )
            return []

        items: list[ConnectorOutput] = []

        for entry in feed.entries[: self.config.max_results]:
            title = entry.get("title", "Untitled")
            url = entry.get("link", "")
            if not url:
                self.logger.debug(f"Skipping entry without URL: {title!r}")
                continue

            author = entry.get("author") or None

            published_at: datetime | None = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
                except (OSError, OverflowError):
                    pass

            # Prefer full content over summary
            raw_html = ""
            if "content" in entry:
                raw_html = entry.content[0].value
            elif "summary" in entry:
                raw_html = entry.summary

            clean_markdown = md(raw_html, heading_style="ATX").strip() if raw_html else ""

            items.append(ConnectorOutput(
                title=title,
                url=url,
                author=author,
                published_at=published_at,
                content=clean_markdown,
                metadata={
                    "feed_title": feed.feed.get("title", ""),
                    "source_type": "rss",
                },
            ))

        self.logger.info(f"Fetched {len(items)} items from {self.config.feed_url}")
        return items
