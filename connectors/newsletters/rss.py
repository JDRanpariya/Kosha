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

class RssNewsletterConnector(BaseConnector):
    ConfigModel = RssConfig

    def fetch(self) -> list[ConnectorOutput]:
        """Fetches the RSS feed and parses it into normalized ConnectorOutput objects."""
        logger.info(f"Fetching RSS feed from: {self.config.feed_url}")

        feed = feedparser.parse(self.config.feed_url)
        items = []

        for entry in feed.entries:
            # 1. Extract standard metadata
            title = entry.get('title', 'Untitled')
            url = entry.get('link', '')
            author = entry.get('author', None)

            # 2. Parse the publication date safely
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
            
            # 3. Get the content (some feeds use 'content', others use 'summary')
            raw_html = ''
            if 'content' in entry:
                raw_html = entry.content[0].value
            elif 'summary' in entry:
                raw_html = entry.summary
                
            # 4. Convert messy HTML into clean Markdown
            clean_markdown = md(raw_html, heading_style="ATX").strip()

            # 5. Package it into your standard schema
            output = ConnectorOutput(
                title=title,
                url=url,
                author=author,
                published_at=published_at,
                content=clean_markdown,
                metadata={
                    "feed_title": feed.feed.get('title', ''),
                    "source_type": "rss"
                }
            )
            items.append(output)

        return items
