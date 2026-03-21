from connectors.papers.arxiv import ArxivConnector
from connectors.newsletters.rss import RssNewsletterConnector
from connectors.newsletters.substack import SubstackConnector
from connectors.newsletters.email_imap import EmailImapConnector
from connectors.social.hackernews import HackerNewsConnector
from connectors.social.reddit import RedditConnector
from connectors.dev.github import GitHubConnector
from connectors.podcasts.spotify import SpotifyPodcastConnector
from connectors.youtube.youtube import YouTubeConnector

CONNECTOR_REGISTRY: dict[str, dict[str, dict]] = {

    # ── Papers ────────────────────────────────────────────────────────────────
    "papers": {
        "arxiv": {
            "class": ArxivConnector,
            "display_name": "arXiv",
            "required_fields": ["categories"],
            "optional_fields": ["max_results"],
            "example_config": {"categories": ["cs.AI", "stat.ML"]},
        },
    },

    # ── Newsletters ───────────────────────────────────────────────────────────
    "newsletters": {
        "rss": {
            "class": RssNewsletterConnector,
            "display_name": "RSS Feed",
            "required_fields": ["feed_url"],
            "optional_fields": ["max_results"],
            "example_config": {"feed_url": "https://example.com/feed.rss"},
        },
        "substack": {
            "class": SubstackConnector,
            "display_name": "Substack",
            "required_fields": ["publication_url"],
            "optional_fields": ["max_results"],
            "example_config": {"publication_url": "https://stratechery.substack.com"},
        },
        "email_imap": {
            "class": EmailImapConnector,
            "display_name": "Newsletter via Email (IMAP)",
            "required_fields": ["imap_host", "username", "password"],
            "optional_fields": [
                "imap_port",
                "mailbox",
                "sender_filter",
                "subject_filter",
                "max_results",
                "mark_as_read",
                "only_unread",
            ],
            "example_config": {
                "imap_host": "imap.gmail.com",
                "username": "you@gmail.com",
                "password": "app-specific-password",
                "sender_filter": "@substack.com",
                "mark_as_read": True,
            },
        },
    },

    # ── Social ────────────────────────────────────────────────────────────────
    "social": {
        "hackernews": {
            "class": HackerNewsConnector,
            "display_name": "Hacker News",
            "required_fields": [],
            "optional_fields": [
                "tags",
                "query",
                "min_points",
                "max_results",
                "sort_by_date",
            ],
            "example_config": {"tags": "front_page", "min_points": 100},
        },
        "reddit": {
            "class": RedditConnector,
            "display_name": "Reddit",
            "required_fields": ["subreddits"],
            "optional_fields": [
                "sort",
                "time_filter",
                "max_results",
                "min_score",
                "include_self_text",
            ],
            "example_config": {
                "subreddits": ["MachineLearning", "LocalLLaMA"],
                "min_score": 50,
            },
        },
        "github": {
            "class": GitHubConnector,
            "display_name": "GitHub Releases & Trending",
            "required_fields": [],
            "optional_fields": [
                "api_token",
                "repos",
                "fetch_releases",
                "fetch_trending",
                "trending_language",
                "trending_since",
                "max_results",
            ],
            "example_config": {
                "repos": ["openai/whisper", "ollama/ollama"],
                "fetch_trending": True,
                "trending_language": "python",
                "trending_since": "weekly",
            },
        },
    },

    # ── Podcasts ──────────────────────────────────────────────────────────────
    "podcasts": {
        "spotify": {
            "class": SpotifyPodcastConnector,
            "display_name": "Spotify Podcasts",
            "required_fields": ["show_id", "client_id", "client_secret"],
            "optional_fields": ["market", "limit"],
            "example_config": {"show_id": "2MAi0BvDc6GTFvKFPXnkCL"},
        },
    },

    # ── Videos ────────────────────────────────────────────────────────────────
    "videos": {
        "youtube": {
            "class": YouTubeConnector,
            "display_name": "YouTube",
            "required_fields": ["api_key", "channels"],
            "optional_fields": ["max_results"],
            "example_config": {
                "channels": ["UCBcRF18a7Qf58cCRy5xuWwQ"],
                "max_results": 10,
            },
        },
    },
}


# ── Public helpers ────────────────────────────────────────────────────────────

def get_connector_class(category: str, source_type: str):
    """Return the connector class for category + type, or None."""
    entry = CONNECTOR_REGISTRY.get(
        category, {}
    ).get(source_type)
    return entry["class"] if entry else None


def list_connectors() -> list[dict]:
    """Flat list of all registered connectors — used by /api/sources/available."""
    result = []
    for category, types in CONNECTOR_REGISTRY.items():
        for source_type, meta in types.items():
            result.append({
                "category": category,
                "type": source_type,
                "display_name": meta["display_name"],
                "required_fields": meta["required_fields"],
                "optional_fields": meta.get("optional_fields", []),
                "example_config": meta.get("example_config", {}),
            })
    return result
