"""
Reddit connector using the public JSON API.
No authentication required for public subreddits.
"""

import httpx
import logging
from datetime import datetime, timezone

from markdownify import markdownify as md

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)

_REDDIT_BASE = "https://www.reddit.com"
_USER_AGENT  = "kosha-aggregator/1.0 (personal open-source content reader)"


class RedditConfig(ConnectorConfig):
    subreddits: list[str]               # ["MachineLearning", "LocalLLaMA"]
    sort: str = "hot"                   # hot | new | top | rising
    time_filter: str = "day"           # hour|day|week|month|year|all (top only)
    max_results: int = 25              # per subreddit
    min_score: int = 10
    include_self_text: bool = True     # include body of text posts


class RedditConnector(BaseConnector):
    """
    Fetches posts from one or more subreddits.

    Example configs
    ---------------
    Hot posts from ML subreddits:
        {"subreddits": ["MachineLearning", "LocalLLaMA"], "min_score": 50}

    Weekly top from a niche subreddit:
        {"subreddits": ["emacs"], "sort": "top", "time_filter": "week"}
    """

    ConfigModel = RedditConfig
    source_type = "reddit"

    def _fetch_subreddit(
        self, client: httpx.Client, subreddit: str
    ) -> list[ConnectorOutput]:
        url = f"{_REDDIT_BASE}/r/{subreddit}/{self.config.sort}.json"
        params: dict = {"limit": self.config.max_results}
        if self.config.sort == "top":
            params["t"] = self.config.time_filter

        self.logger.info(f"Fetching r/{subreddit} ({self.config.sort})")

        try:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                self.logger.warning(f"Subreddit not found: r/{subreddit}")
            else:
                self.logger.error(f"HTTP error for r/{subreddit}: {exc}")
            return []
        except httpx.HTTPError as exc:
            self.logger.error(f"HTTP error for r/{subreddit}: {exc}")
            return []

        items: list[ConnectorOutput] = []

        for wrapper in data.get("data", {}).get("children", []):
            post = wrapper.get("data", {})
            if not post:
                continue

            # Skip stickied mod posts
            if post.get("stickied"):
                continue

            score = post.get("score", 0)
            if score < self.config.min_score:
                continue

            is_self = post.get("is_self", False)
            external_url = post.get("url", "")
            reddit_url = f"https://reddit.com{post.get('permalink', '')}"

            # For self/text posts the canonical URL is the Reddit thread itself
            url = reddit_url if is_self else (external_url or reddit_url)

            created_utc = post.get("created_utc")
            published_at: datetime | None = (
                datetime.fromtimestamp(created_utc, tz=timezone.utc).replace(tzinfo=None)
                if created_utc
                else None
            )

            content_parts: list[str] = []

            if is_self and self.config.include_self_text:
                raw = post.get("selftext", "")
                if raw and raw not in ("[removed]", "[deleted]"):
                    content_parts.append(md(raw).strip())

            if not is_self and external_url:
                content_parts.append(f"**Link:** {external_url}")

            content_parts.append(
                f"**Score:** {score:,} | "
                f"**Comments:** {post.get('num_comments', 0):,} | "
                f"**Thread:** {reddit_url}"
            )

            flair = post.get("link_flair_text") or post.get("author_flair_text") or ""

            items.append(ConnectorOutput(
                title=post.get("title", "Untitled"),
                url=url,
                author=post.get("author"),
                published_at=published_at,
                content="\n\n".join(p for p in content_parts if p),
                metadata={
                    "source_type": "social",
                    "platform": "reddit",
                    "subreddit": subreddit,
                    "score": score,
                    "upvote_ratio": post.get("upvote_ratio", 0.0),
                    "num_comments": post.get("num_comments", 0),
                    "reddit_url": reddit_url,
                    "is_self": is_self,
                    "flair": flair,
                    "post_id": post.get("id"),
                },
            ))

        return items

    def fetch(self) -> list[ConnectorOutput]:
        all_items: list[ConnectorOutput] = []

        with httpx.Client(
            headers={"User-Agent": _USER_AGENT},
            follow_redirects=True,
            timeout=15,
        ) as client:
            for subreddit in self.config.subreddits:
                sub_items = self._fetch_subreddit(client, subreddit)
                all_items.extend(sub_items)
                self.logger.info(
                    f"r/{subreddit}: {len(sub_items)} posts fetched"
                )

        self.logger.info(
            f"Reddit connector: {len(all_items)} total posts "
            f"from {len(self.config.subreddits)} subreddit(s)"
        )
        return all_items
