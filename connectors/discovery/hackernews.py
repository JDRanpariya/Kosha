"""
Hacker News connector via the Algolia Search API.

No authentication required.
API docs: https://hn.algolia.com/api
"""

import httpx
import logging
from datetime import datetime, timezone

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"


class HackerNewsConfig(ConnectorConfig):
    tags: str = "front_page"        # front_page | story | ask_hn | show_hn | job
    query: str = ""                 # optional keyword filter
    min_points: int = 0             # drop posts below this score
    max_results: int = 30
    sort_by_date: bool = False      # True = newest first, False = by relevance


class HackerNewsConnector(BaseConnector):
    """
    Fetches HN stories from the Algolia API.

    Example configs
    ---------------
    Front page top stories:
        {"tags": "front_page", "min_points": 100}

    Ask HN posts:
        {"tags": "ask_hn", "sort_by_date": true, "max_results": 20}

    Keyword search:
        {"tags": "story", "query": "LLM inference", "min_points": 50}
    """

    ConfigModel = HackerNewsConfig
    source_type = "hackernews"

    def fetch(self) -> list[ConnectorOutput]:
        endpoint = _DATE_URL if self.config.sort_by_date else _SEARCH_URL
        params: dict = {
            "tags": self.config.tags,
            "hitsPerPage": self.config.max_results,
        }
        if self.config.query:
            params["query"] = self.config.query

        self.logger.info(
            f"Fetching HN: tags={self.config.tags!r} "
            f"query={self.config.query!r} min_points={self.config.min_points}"
        )

        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(endpoint, params=params)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            self.logger.error(f"HTTP error: {exc}")
            return []

        items: list[ConnectorOutput] = []

        for hit in data.get("hits", []):
            points = hit.get("points") or 0
            if points < self.config.min_points:
                continue

            object_id = hit.get("objectID", "")
            hn_url = f"https://news.ycombinator.com/item?id={object_id}"
            # External link stories have a URL; text posts don't
            url = hit.get("url") or hn_url

            published_at: datetime | None = None
            if created_at := hit.get("created_at"):
                try:
                    published_at = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    ).astimezone(timezone.utc).replace(tzinfo=None)
                except ValueError:
                    pass

            content_parts: list[str] = []
            if story_text := hit.get("story_text"):
                content_parts.append(story_text)
            content_parts.append(
                f"Points: {points} | "
                f"Comments: {hit.get('num_comments', 0)} | "
                f"Discussion: {hn_url}"
            )

            items.append(ConnectorOutput(
                title=hit.get("title", "Untitled"),
                url=url,
                author=hit.get("author"),
                published_at=published_at,
                content="\n\n".join(content_parts),
                metadata={
                    "source_type": "social",
                    "platform": "hackernews",
                    "points": points,
                    "num_comments": hit.get("num_comments", 0),
                    "hn_id": object_id,
                    "hn_url": hn_url,
                    "tags": hit.get("_tags", []),
                },
            ))

        self.logger.info(f"Fetched {len(items)} HN stories")
        return items
