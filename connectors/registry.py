# connectors/registry.py

from connectors.papers.arxiv import ArxivConnector
from connectors.newsletters.rss import RssNewsletterConnector

CONNECTOR_REGISTRY = {
    "papers": {
        "arxiv": {
            "class": ArxivConnector,
            "display_name": "arXiv",
            "required_fields": ["categories"],
        },
    },
    "newsletters": {
        "rss": {
            "class": RssNewsletterConnector,
            "display_name": "RSS Newsletter",
            "required_fields": ["feed_url"],
        },
    },
}

# Optional connectors — only register if dependencies are installed

try:
    from connectors.podcasts.spotify import SpotifyPodcastConnector
    CONNECTOR_REGISTRY["podcasts"] = {
        "spotify": {
            "class": SpotifyPodcastConnector,
            "display_name": "Spotify Podcasts",
            "required_fields": ["show_id", "client_id", "client_secret"],
        },
    }
except ImportError:
    pass

try:
    from connectors.youtube.youtube import YouTubeConnector
    CONNECTOR_REGISTRY["videos"] = {
        "youtube": {
            "class": YouTubeConnector,
            "display_name": "YouTube",
            "required_fields": ["api_key", "channel_ids"],
        },
    }
except ImportError:
    pass
