"""
Reddit connector via the public JSON API.

No authentication required — uses Reddit's anonymous JSON endpoints,
which are stable and rate-limit-friendly for read-only access.

API reference:
  https://www.reddit.com/dev/api
  https://reddit.com/r/{subreddit}.json?limit=25&t=day

Rate limits (unauthenticated):
  ~60 requests/minute. Each fetch() call makes 1 request per subreddit.
  For large configs (10+ subreddits) consider OAuth in Phase 2.

Listing modes:
  hot   — Reddit's ranking algorithm (default)
  new   — chronological, newest first
  top   — highest-scoring (combine with time_filter)
  rising — gaining traction quickly

Time filters (only meaningful for `top` and `controversial`):
  hour | day | week | month | year | all
"""

import httpx
import logging
from datetime import datetime, timezone

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.reddit.com"
# Reddit blocks the default httpx User-Agent; a custom one avoids 429s.
_HEADERS = {
    "User-Agent": "Kosha/0.1 (personal content aggregator; +https://github.com/kosha)"}


class RedditConfig(ConnectorConfig):
    # e.g. ["MachineLearning", "LocalLLaMA"]
    subreddits: list[str]
    listing: str = "hot"                  # hot | new | top | rising
    time_filter: str = "day"              # hour | day | week | month | year | all
    min_score: int = 0                    # drop posts below this upvote count
    max_results: int = 25                 # per subreddit (Reddit max = 100)
    include_self_text: bool = True        # include text-post body in content
    exclude_nsfw: bool = True             # skip posts marked NSFW


class RedditConnector(BaseConnector):
    """
    Fetches posts from one or more subreddits using Reddit's public JSON API.

    Example configs
    ---------------
    Top ML posts from the past week:
        {
            "subreddits": ["MachineLearning", "LocalLLaMA"],
            "listing": "top",
            "time_filter": "week",
            "min_score": 50
        }

    Hot posts from multiple communities, no NSFW:
        {
            "subreddits": ["philosophy", "slatestarcodex", "artificial"],
            "listing": "hot",
            "max_results": 20
        }

    Rising posts to catch early discussions:
        {
            "subreddits": ["singularity"],
            "listing": "rising",
            "min_score": 10
        }
    """

    ConfigModel = RedditConfig
    source_type = "reddit"

    def _fetch_subreddit(
        self,
        client: httpx.Client,
        subreddit: str,
    ) -> list[ConnectorOutput]:
        """Fetch posts from a single subreddit and return ConnectorOutput list."""
        listing = self.config.listing
        params: dict = {
            "limit": min(self.config.max_results, 100),
        }
        # time_filter only applies to certain listing types
        if listing in ("top", "controversial"):
            params["t"] = self.config.time_filter

        url = f"{_BASE_URL}/r/{subreddit}/{listing}.json"

        try:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                self.logger.warning(f"Subreddit r/{subreddit} not found (404)")
            else:
                self.logger.error(
                    f"HTTP {exc.response.status_code} fetching r/{subreddit}: {exc}")
            return []
        except httpx.HTTPError as exc:
            self.logger.error(f"Network error fetching r/{subreddit}: {exc}")
            return []

        posts = data.get("data", {}).get("children", [])
        items: list[ConnectorOutput] = []

        for child in posts:
            post = child.get("data", {})

            # ── Filters ──────────────────────────────────────────────────────

            # Skip stickied mod posts — usually announcements, not content
            if post.get("stickied"):
                continue

            # Respect NSFW filter
            if self.config.exclude_nsfw and post.get("over_18"):
                continue

            score = post.get("score", 0)
            if score < self.config.min_score:
                continue

            # ── Metadata ─────────────────────────────────────────────────────

            post_id = post.get("id", "")
            permalink = post.get("permalink", "")
            reddit_url = f"{_BASE_URL}{permalink}" if permalink else ""

            # External link posts have a URL; self posts point back to Reddit
            is_self = post.get("is_self", False)
            external_url = post.get("url", "") if not is_self else ""
            # Canonical URL: external link when available, otherwise the discussion
            url = external_url if external_url and not external_url.startswith(
                _BASE_URL) else reddit_url

            # ── Author ───────────────────────────────────────────────────────

            author = post.get("author")
            # Deleted/removed authors show as [deleted]
            if author in ("[deleted]", "AutoModerator", None):
                author = None

            # ── Published date ────────────────────────────────────────────────

            published_at: datetime | None = None
            if created_utc := post.get("created_utc"):
                try:
                    published_at = datetime.fromtimestamp(
                        float(created_utc), tz=timezone.utc
                    ).replace(tzinfo=None)
                except (ValueError, OSError):
                    pass

            # ── Content ──────────────────────────────────────────────────────

            content_parts: list[str] = []

            # Text post body (self-text) — can contain Markdown
            if self.config.include_self_text and is_self:
                self_text = post.get("selftext", "").strip()
                # Reddit uses "[removed]" / "[deleted]" for moderated posts
                if self_text and self_text not in ("[removed]", "[deleted]"):
                    content_parts.append(self_text)

            # Post flair — useful for categorisation signals
            flair = post.get("link_flair_text") or post.get(
                "author_flair_text")

            # Stats footer — mirrors what HackerNews connector does
            num_comments = post.get("num_comments", 0)
            content_parts.append(
                f"Score: {score} | Comments: {num_comments} | "
                f"Discussion: {reddit_url}"
            )

            # ── Output ───────────────────────────────────────────────────────

            items.append(ConnectorOutput(
                title=post.get("title", "Untitled"),
                url=url or reddit_url,
                author=f"u/{author}" if author else None,
                published_at=published_at,
                content="\n\n".join(content_parts),
                metadata={
                    "source_type": "social",
                    "platform": "reddit",
                    "subreddit": post.get("subreddit", subreddit),
                    "post_id": post_id,
                    "reddit_url": reddit_url,
                    "score": score,
                    "num_comments": num_comments,
                    "is_self": is_self,
                    "flair": flair,
                    "listing": listing,
                    "thumbnail": post.get("thumbnail") or None,
                },
            ))

        return items

    def fetch(self) -> list[ConnectorOutput]:
        """Fetch posts from all configured subreddits."""
        self.logger.info(
            f"Fetching Reddit: subreddits={self.config.subreddits} "
            f"listing={self.config.listing} min_score={self.config.min_score}"
        )

        results: list[ConnectorOutput] = []

        with httpx.Client(headers=_HEADERS, timeout=15, follow_redirects=True) as client:
            for subreddit in self.config.subreddits:
                items = self._fetch_subreddit(client, subreddit)
                results.extend(items)
                self.logger.info(f"r/{subreddit}: fetched {len(items)} posts")

        self.logger.info(f"Reddit connector: {len(results)} total posts across {
                         len(self.config.subreddits)} subreddit(s)")
        return results
