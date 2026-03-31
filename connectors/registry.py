from connectors.subscriptions.rss import RssNewsletterConnector
from connectors.subscriptions.substack import SubstackConnector
from connectors.subscriptions.email_imap import EmailImapConnector
from connectors.subscriptions.arxiv import ArxivConnector
from connectors.subscriptions.youtube import YouTubeConnector
from connectors.discovery.hackernews import HackerNewsConnector
from connectors.discovery.reddit import RedditConnector

CONNECTOR_REGISTRY: dict[str, dict[str, dict]] = {

    # ── Subscriptions (content comes TO you) ──────────────────────────────────
    "subscriptions": {
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
                "imap_port", "mailbox", "sender_filter",
                "subject_filter", "max_results", "mark_as_read", "only_unread",
            ],
            "example_config": {
                "imap_host": "imap.gmail.com",
                "username": "you@gmail.com",
                "password": "app-specific-password",
                "sender_filter": "@substack.com",
                "mark_as_read": True,
            },
        },
        "arxiv": {
            "class": ArxivConnector,
            "display_name": "arXiv",
            "required_fields": ["categories"],
            "optional_fields": ["max_results"],
            "example_config": {"categories": ["cs.AI", "stat.ML"]},
        },
        "youtube": {
            "class": YouTubeConnector,
            "display_name": "YouTube Channel",
            "required_fields": ["api_key", "channels"],
            "optional_fields": ["max_results"],
            "example_config": {
                "channels": ["UCBcRF18a7Qf58cCRy5xuWwQ"],
                "max_results": 10,
            },
        },
    },

    # ── Discovery (you go TO the content) ─────────────────────────────────────
    "discovery": {
        "hackernews": {
            "class": HackerNewsConnector,
            "display_name": "Hacker News",
            "required_fields": [],
            "optional_fields": [
                "tags", "query", "min_points", "max_results", "sort_by_date",
            ],
            "example_config": {"tags": "front_page", "min_points": 100},
        },
        "reddit": {
            "class": RedditConnector,
            "display_name": "Reddit",
            "required_fields": ["subreddits"],
            "optional_fields": [
                "listing", "time_filter", "min_score",
                "max_results", "include_self_text", "exclude_nsfw",
            ],
            "example_config": {
                "subreddits": ["MachineLearning", "LocalLLaMA"],
                "listing": "top",
                "time_filter": "week",
                "min_score": 50,
            },
        },
    },
}


# ── Public helpers ────────────────────────────────────────────────────────────

def get_connector_class(category: str, source_type: str):
    entry = CONNECTOR_REGISTRY.get(category, {}).get(source_type)
    return entry["class"] if entry else None


def list_connectors() -> list[dict]:
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
