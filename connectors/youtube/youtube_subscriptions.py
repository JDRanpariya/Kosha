"""
YouTube Subscriptions connector using OAuth 2.0.

Fetches recent uploads from every channel the authenticated user subscribes to.

### Setup

1. Google Cloud Console → APIs & Services → Credentials

   → Create OAuth 2.0 Client ID  (Web application type)

2. Add authorised redirect URI:

     http://localhost:8000/api/youtube/oauth/callback   (dev)
     https://your-domain.com/api/youtube/oauth/callback (prod)

3. Create secret files:

     infra/secrets/youtube_client_id.txt      ← OAuth client ID
     infra/secrets/youtube_client_secret.txt  ← OAuth client secret
   These are DIFFERENT from the Data API key used by YouTubeConnector.

The source is created automatically when the user completes the OAuth flow
from the Sources page. Do not configure this type manually.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from markdownify import markdownify as md
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)


class YouTubeSubscriptionsConfig(ConnectorConfig):
    access_token: str
    refresh_token: str = ""
    client_id: str = ""
    client_secret: str = ""
    max_videos_per_channel: int = 5
    max_channels: int = 100   # cap to keep quota usage manageable


class YouTubeSubscriptionsConnector(BaseConnector):
    """
    Reads the authenticated user's YouTube subscriptions list then
    pulls the N most recent uploads from each channel in one batch.

    Quota cost estimate (default settings, 100 channels, 5 videos each):

      - subscriptions.list : ~2 units × pages  ≈  2–4
      - channels.list      : 1 unit × 100      = 100

      - playlistItems.list : 1 unit × 100      = 100
      - videos.list        : 1 unit × batches  ≈  10

      Total                                    ≈  214  (well under 10 000/day)
    """

    ConfigModel = YouTubeSubscriptionsConfig
    source_type = "youtube_subscriptions"

    # ── private helpers ───────────────────────────────────────────────────────

    def _build_client(self):
        creds = Credentials(
            token=self.config.access_token,
            refresh_token=self.config.refresh_token or None,
            client_id=self.config.client_id or None,
            client_secret=self.config.client_secret or None,
            token_uri="https://oauth2.googleapis.com/token",
        )
        return build("youtube", "v3", credentials=creds, cache_discovery=False)

    def _get_subscribed_channel_ids(self, youtube) -> list[str]:
        """Page through subscriptions.list to collect all channel IDs."""
        channel_ids: list[str] = []
        next_page_token: str | None = None

        while len(channel_ids) < self.config.max_channels:
            try:
                params: dict[str, Any] = {
                    "part": "snippet",
                    "mine": True,
                    "maxResults": 50,
                }
                if next_page_token:
                    params["pageToken"] = next_page_token

                resp = youtube.subscriptions().list(**params).execute()
            except HttpError as exc:
                self.logger.error(f"Error fetching subscriptions: {exc}")
                break

            for item in resp.get("items", []):
                cid = item["snippet"]["resourceId"]["channelId"]
                channel_ids.append(cid)
                if len(channel_ids) >= self.config.max_channels:
                    break

            next_page_token = resp.get("nextPageToken")
            if not next_page_token:
                break

        self.logger.info(f"Found {len(channel_ids)} subscribed channels")
        return channel_ids

    def _get_uploads_playlist_ids(
        self, youtube, channel_ids: list[str]
    ) -> dict[str, str]:
        """
        Batch-fetch uploads playlist IDs for all channels.
        channels.list accepts up to 50 IDs per call.
        Returns {channel_id: uploads_playlist_id}.
        """
        result: dict[str, str] = {}
        for i in range(0, len(channel_ids), 50):
            batch = channel_ids[i : i + 50]
            try:
                resp = (
                    youtube.channels()
                    .list(part="contentDetails", id=",".join(batch))
                    .execute()
                )
            except HttpError as exc:
                self.logger.error(f"Error fetching channel details: {exc}")
                continue

            for item in resp.get("items", []):
                cid = item["id"]
                pid = item["contentDetails"]["relatedPlaylists"]["uploads"]
                result[cid] = pid

        return result

    def _get_recent_video_ids(
        self, youtube, playlist_id: str
    ) -> list[str]:
        """Fetch the N most recent video IDs from an uploads playlist."""
        try:
            resp = (
                youtube.playlistItems()
                .list(
                    part="contentDetails",
                    playlistId=playlist_id,
                    maxResults=min(self.config.max_videos_per_channel, 50),
                )
                .execute()
            )
        except HttpError as exc:
            self.logger.error(f"Error fetching playlist {playlist_id}: {exc}")
            return []

        return [
            item["contentDetails"]["videoId"]
            for item in resp.get("items", [])
        ]

    def _get_video_details(
        self, youtube, video_ids: list[str]
    ) -> dict[str, dict]:
        """Batch fetch full video details for up to 50 IDs at once."""
        if not video_ids:
            return {}
        result: dict[str, dict] = {}
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i : i + 50]
            try:
                resp = (
                    youtube.videos()
                    .list(
                        part="snippet,statistics,contentDetails",
                        id=",".join(batch),
                    )
                    .execute()
                )
            except HttpError as exc:
                self.logger.error(f"Error fetching video details: {exc}")
                continue
            for item in resp.get("items", []):
                result[item["id"]] = item
        return result

    def _build_output(self, video_id: str, detail: dict) -> ConnectorOutput:
        snippet    = detail.get("snippet", {})
        statistics = detail.get("statistics", {})
        content_details = detail.get("contentDetails", {})

        url    = f"https://www.youtube.com/watch?v={video_id}"
        author = snippet.get("channelTitle", "Unknown Channel")

        published_at: datetime | None = None
        raw_date = snippet.get("publishedAt")
        if raw_date:
            try:
                published_at = (
                    datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                    .astimezone(timezone.utc)
                    .replace(tzinfo=None)
                )
            except ValueError:
                pass

        raw_desc = snippet.get("description", "")
        content  = md(raw_desc).strip() if raw_desc else ""

        thumbnails   = snippet.get("thumbnails", {})
        thumbnail_url = (
            thumbnails.get("maxres", {}).get("url")
            or thumbnails.get("high", {}).get("url")
            or thumbnails.get("default", {}).get("url")
        )

        return ConnectorOutput(
            title=snippet.get("title", "Untitled Video"),
            url=url,
            author=author,
            published_at=published_at,
            content=content,
            metadata={
                "source_type": "video",
                "platform": "youtube_subscriptions",
                "video_id": video_id,
                "channel_id": snippet.get("channelId"),
                "channel_title": author,
                "thumbnail_url": thumbnail_url,
                "duration_iso": content_details.get("duration"),
                "view_count": statistics.get("viewCount"),
                "like_count": statistics.get("likeCount"),
                "comment_count": statistics.get("commentCount"),
                "tags": snippet.get("tags", []),
            },
        )

    # ── main entry point ──────────────────────────────────────────────────────

    def fetch(self) -> list[ConnectorOutput]:
        youtube = self._build_client()

        channel_ids = self._get_subscribed_channel_ids(youtube)
        if not channel_ids:
            self.logger.warning("No subscribed channels found")
            return []

        playlist_map = self._get_uploads_playlist_ids(youtube, channel_ids)

        # Collect all video IDs across all channels
        all_video_ids: list[str] = []
        for cid in channel_ids:
            pid = playlist_map.get(cid)
            if pid:
                all_video_ids.extend(self._get_recent_video_ids(youtube, pid))

        self.logger.info(
            f"Fetching details for {len(all_video_ids)} videos "
            f"from {len(channel_ids)} channels"
        )

        video_details = self._get_video_details(youtube, all_video_ids)

        items: list[ConnectorOutput] = []
        for vid in all_video_ids:
            detail = video_details.get(vid)
            if detail:
                items.append(self._build_output(vid, detail))

        self.logger.info(
            f"YouTube Subscriptions: {len(items)} videos from "
            f"{len(channel_ids)} channels"
        )
        return items
