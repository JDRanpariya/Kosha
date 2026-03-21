import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
from datetime import datetime
from markdownify import markdownify as md

from connectors.base import BaseConnector, ConnectorConfig
from schemas.connector_output import ConnectorOutput

logger = logging.getLogger(__name__)

class SpotifyConfig(ConnectorConfig):
    show_id: str  # The Spotify ID for the podcast
    client_id: str
    client_secret: str
    market: str = "US"
    limit: int = 10

class SpotifyPodcastConnector(BaseConnector):
    ConfigModel = SpotifyConfig

    def _get_client(self):
        """Authenticates with Spotify using Client Credentials Flow."""
        auth_manager = SpotifyClientCredentials(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret
        )
        return spotipy.Spotify(auth_manager=auth_manager)

    def fetch(self) -> list[ConnectorOutput]:
        """Fetches the latest episodes from a specific Spotify Show."""
        sp = self._get_client()
        
        logger.info(f"Fetching Spotify episodes for show: {self.config.show_id}")
        
        # 1. Get show metadata and episodes
        results = sp.show_episodes(
            self.config.show_id, 
            limit=self.config.limit, 
            market=self.config.market
        )
        
        items = []
        for episode in results['items']:
            # 2. Extract Metadata
            title = episode.get('name', 'Untitled Episode')
            url = episode.get('external_urls', {}).get('spotify', '')
            
            # 3. Parse Date (Spotify uses YYYY-MM-DD)
            release_date_str = episode.get('release_date')
            published_at = None
            if release_date_str:
                published_at = datetime.strptime(release_date_str, "%Y-%m-%d")

            # 4. Content (Description)
            # Spotify descriptions are often plain text or basic HTML
            raw_description = episode.get('description', '')
            clean_markdown = md(raw_description).strip()

            # 5. Package into ConnectorOutput
            output = ConnectorOutput(
                title=title,
                url=url,
                author=None, # For podcasts, the 'Show' is the author
                published_at=published_at,
                content=clean_markdown,
                metadata={
                    "duration_ms": episode.get('duration_ms'),
                    "explicit": episode.get('explicit'),
                    "images": episode.get('images', []),
                    "source_type": "audio"
                }
            )
            items.append(output)

        return items
