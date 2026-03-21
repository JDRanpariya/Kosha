import feedparser
import logging
from datetime import datetime
from time import mktime
from markdownify import markdownify as md

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)

class ArxivConfig(ConnectorConfig):
    # Categories like ["cs.AI", "stat.ML"]
    categories: list[str]

class ArxivConnector(BaseConnector):
    ConfigModel = ArxivConfig

    def fetch(self) -> list[ConnectorOutput]:
        """Fetches the daily arXiv RSS feed for specific categories."""
        # 1. Build the official RSS URL
        # Format: https://rss.arxiv.org/rss/cs.AI+stat.ML
        cat_string = "+".join(self.config.categories)
        rss_url = f"https://rss.arxiv.org/rss/{cat_string}"
        
        logger.info(f"Fetching daily arXiv RSS: {rss_url}")
        feed = feedparser.parse(rss_url)
        items = []

        if feed.bozo:
            logger.error(f"Error parsing arXiv RSS: {feed.bozo_exception}")

        for entry in feed.entries:
            # 2. Extract Metadata
            # arXiv RSS titles usually look like: "Title. (arXiv:2401.12345v1 [cs.AI])"
            # We clean up the title to remove the ID suffix if you prefer it clean.
            title = entry.get('title', 'Untitled').split(' (arXiv:')[0].strip()
            
            url = entry.get('link', '')
            
            # 3. Authors (arXiv RSS provides them in the 'author' or 'authors' field)
            # feedparser usually normalizes this to 'author'
            author_str = entry.get('author', 'Unknown')

            # 4. Publication Date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
            else:
                published_at = datetime.now() # Fallback for daily feed

            # 5. Content (The Abstract)
            # In the RSS feed, the abstract is in the 'summary' or 'description'
            raw_summary = entry.get('summary', '') or entry.get('description', '')
            
            # Clean the abstract: arXiv RSS summaries often start with "Abstract: "
            clean_abstract = md(raw_summary).replace('Abstract: ', '').strip()

            # 6. Package into standard schema
            output = ConnectorOutput(
                title=title,
                url=url,
                author=author_str,
                published_at=published_at,
                content=clean_abstract,
                metadata={
                    "arxiv_categories": self.config.categories,
                    "feed_source": "official_rss",
                    "source_type": "papers"
                }
            )
            items.append(output)

        return items
