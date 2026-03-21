# connectors/youtube/youtube.py
"""
YouTube connector using the Data API v3.

Fetches recent uploads from specified channels using an API key.
No OAuth needed — only public data is accessed.

Quota note: each channel costs ~3 units (1 channels.list + 1 playlistItems.list).
Default quota is 10,000 units/day, so ~3,000 channels/day is the ceiling.
"""

import logging
from datetime import datetime, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from markdownify import markdownify as md

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)


class YouTubeConfig(ConnectorConfig):
    api_key: str
    channels: list[str]   # Channel IDs, e.g. ["UCBcRF18a7Qf58cCRy5xuWwQ"]
    max_results: int = 10  # Videos to fetch per channel (max 50 per API call)


class YouTubeConnector(BaseConnector):
    """
    Fetches the latest videos from a list of YouTube channel IDs
    using the YouTube Data API v3.

    Getting a channel ID:
      - Go to the channel page
      - View page source, search for "channelId"
      - Or use: https://www.youtube.com/@ChannelHandle/about

        and inspect the canonical URL
    """

    ConfigModel = YouTubeConfig

    def _build_client(self):
        """Create an authenticated YouTube API client."""
        return build(
            "youtube",
            "v3",
            developerKey=self.config.api_key,
            # Disable file-based cache (avoids warning noise in server envs)
            cache_discovery=False,
        )

    def _get_uploads_playlist_id(
        self,
        youtube,
        channel_id: str,
    ) -> str | None:
        """
        Every YouTube channel has a hidden 'uploads' playlist.
        This is the most reliable way to paginate a channel's videos.
        """
        try:
            response = (
                youtube.channels()
                .list(part="contentDetails", id=channel_id)
                .execute()
            )
        except HttpError as e:
            logger.error(f"API error fetching channel '{channel_id}': {e}")
            return None

        items = response.get("items", [])
        if not items:
            logger.warning(
                f"Channel ID '{channel_id}' not found or has no content. "
                "Check that the ID is correct (not a @handle)."
            )
            return None

        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _get_playlist_video_ids(
        self,
        youtube,
        playlist_id: str,
    ) -> list[str]:
        """
        Fetches video IDs from a playlist (the uploads playlist).
        Returns at most self.config.max_results IDs.
        """
        try:
            response = (
                youtube.playlistItems()
                .list(
                    part="contentDetails",
                    playlistId=playlist_id,
                    maxResults=min(self.config.max_results, 50),
                )
                .execute()
            )
        except HttpError as e:
            logger.error(f"API error fetching playlist '{playlist_id}': {e}")
            return []

        return [
            item["contentDetails"]["videoId"]
            for item in response.get("items", [])
            if "contentDetails" in item
        ]

    def _get_video_details(
        self,
        youtube,
        video_ids: list[str],
    ) -> dict[str, dict]:
        """
        Batch-fetches full video details (snippet + statistics + contentDetails).
        Returns a dict keyed by video ID.
        One API call for up to 50 videos — much cheaper than one call per video.
        """
        if not video_ids:
            return {}
        try:
            response = (
                youtube.videos()
                .list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(video_ids),
                )
                .execute()
            )
        except HttpError as e:
            logger.error(f"API error fetching video details: {e}")
            return {}

        return {item["id"]: item for item in response.get("items", [])}

    def fetch(self) -> list[ConnectorOutput]:
        """
        Main entry point. Iterates over configured channels and returns
        a flat list of ConnectorOutput objects.
        """
        youtube = self._build_client()
        results: list[ConnectorOutput] = []

        for channel_id in self.config.channels:
            logger.info(f"Processing YouTube channel: {channel_id}")

            # Step 1 — resolve channel → uploads playlist
            playlist_id = self._get_uploads_playlist_id(youtube, channel_id)
            if not playlist_id:
                continue  # logged inside helper

            # Step 2 — get recent video IDs from that playlist
            video_ids = self._get_playlist_video_ids(youtube, playlist_id)
            if not video_ids:
                logger.warning(f"No videos found in playlist for channel: {channel_id}")
                continue

            # Step 3 — batch-fetch full details (1 API call for all videos)
            video_details = self._get_video_details(youtube, video_ids)

            # Step 4 — build ConnectorOutput for each video
            for video_id in video_ids:
                detail = video_details.get(video_id)
                if not detail:
                    logger.debug(f"Missing detail for video {video_id}, skipping")
                    continue

                snippet = detail.get("snippet", {})
                statistics = detail.get("statistics", {})
                content_details = detail.get("contentDetails", {})

                # --- URL ---
                url = f"https://www.youtube.com/watch?v={video_id}"

                # --- Author (channel name, not individual person) ---
                author = snippet.get("channelTitle", "Unknown Channel")

                # --- Published date (YouTube returns ISO 8601 with Z suffix) ---
                published_at: datetime | None = None
                raw_date = snippet.get("publishedAt")
                if raw_date:
                    try:
                        published_at = datetime.fromisoformat(
                            raw_date.replace("Z", "+00:00")
                        ).astimezone(timezone.utc).replace(tzinfo=None)
                        # Store as naive UTC to match other connectors
                    except ValueError:
                        logger.debug(f"Could not parse date '{raw_date}' for {video_id}")

                # --- Content (video description → Markdown) ---
                raw_description = snippet.get("description", "")
                clean_content = md(raw_description).strip() if raw_description else ""

                # --- Thumbnail (prefer high quality) ---
                thumbnails = snippet.get("thumbnails", {})
                thumbnail_url = (
                    thumbnails.get("maxres", {}).get("url")
                    or thumbnails.get("high", {}).get("url")
                    or thumbnails.get("default", {}).get("url")
                )

                output = ConnectorOutput(
                    title=snippet.get("title", "Untitled Video"),
                    url=url,
                    author=author,
                    published_at=published_at,
                    content=clean_content,
                    metadata={
                        "source_type": "video",
                        "video_id": video_id,
                        "channel_id": channel_id,
                        "channel_title": author,
                        "thumbnail_url": thumbnail_url,
                        "duration_iso": content_details.get("duration"),  # e.g. "PT12M34S"
                        "view_count": statistics.get("viewCount"),
                        "like_count": statistics.get("likeCount"),
                        "comment_count": statistics.get("commentCount"),
                        "tags": snippet.get("tags", []),
                        "category_id": snippet.get("categoryId"),
                    },
                )
                results.append(output)

            logger.info(
                f"Channel {channel_id}: fetched {len(video_ids)} video(s)"
            )

        return results
