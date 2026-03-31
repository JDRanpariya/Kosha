"""
Substack connector — thin wrapper around RssNewsletterConnector.

Every Substack publication exposes a standard RSS feed at:
    https://{slug}.substack.com/feed

Accepts either:
  - A slug:           "stratechery"
  - A full URL:       "https://stratechery.com"  or

                      "https://stratechery.substack.com"
"""

from connectors.base import ConnectorConfig
from connectors.subscriptions.rss import RssNewsletterConnector
from schemas.connector_output import ConnectorOutput


class SubstackConfig(ConnectorConfig):
    publication_url: str    # slug or full URL
    max_results: int = 20


class SubstackConnector(RssNewsletterConnector):
    ConfigModel = SubstackConfig
    source_type = "substack"

    def __init__(self, config: dict) -> None:
        raw = config.get("publication_url", "")
        feed_url = self._resolve(raw)
        # Inject resolved feed_url so the parent RSS connector works correctly
        super().__init__({**config, "feed_url": feed_url})

    @staticmethod
    def _resolve(publication_url: str) -> str:
        url = publication_url.strip().rstrip("/")
        if not url:
            raise ValueError("publication_url is required for SubstackConnector")
        if url.startswith("http"):
            return url if url.endswith("/feed") else f"{url}/feed"
        # bare slug → assume *.substack.com
        return f"https://{url}.substack.com/feed"

    def fetch(self) -> list[ConnectorOutput]:
        items = super().fetch()
        for item in items:
            item.metadata["source_type"] = "substack"
            item.metadata["platform"] = "substack"
        return items
