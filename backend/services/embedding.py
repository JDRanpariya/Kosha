# backend/services/embedding.py

"""
Embedding service - singleton for SentenceTransformer model.
Handles all embedding operations across the application.
"""

from functools import lru_cache
from typing import TYPE_CHECKING

from backend.core.constants import EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION
from backend.core.logging import get_logger

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)


class EmbeddingService:
    """
    Singleton service for generating text embeddings.
    Lazily loads the model on first use.
    """
    
    _instance: "EmbeddingService | None" = None
    _model: "SentenceTransformer | None" = None
    _available: bool | None = None
    
    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def available(self) -> bool:
        """Check if embedding functionality is available."""
        if self._available is None:
            self._available = self._check_availability()
        return self._available
    
    @property
    def model(self) -> "SentenceTransformer | None":
        """Lazily load and return the model."""
        if not self.available:
            return None
        if self._model is None:
            self._model = self._load_model()
        return self._model
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return EMBEDDING_DIMENSION
    
    def _check_availability(self) -> bool:
        """Check if sentence-transformers is installed."""
        try:
            import sentence_transformers  # noqa
            return True
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Embedding features will be disabled."
            )
            return False
    
    def _load_model(self) -> "SentenceTransformer":
        """Load the SentenceTransformer model."""
        from sentence_transformers import SentenceTransformer
        
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Embedding model loaded successfully")
        return model
    
    def encode(
        self,
        text: str,
        show_progress_bar: bool = False,
    ) -> list[float] | None:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            show_progress_bar: Show progress during encoding
            
        Returns:
            List of floats (embedding vector) or None if unavailable
        """
        if not self.available or not text:
            return None
        
        try:
            embedding = self.model.encode(
                text,
                show_progress_bar=show_progress_bar,
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def encode_batch(
        self,
        texts: list[str],
        show_progress_bar: bool = True,
    ) -> list[list[float]] | None:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            show_progress_bar: Show progress during encoding
            
        Returns:
            List of embedding vectors or None if unavailable
        """
        if not self.available or not texts:
            return None
        
        try:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=show_progress_bar,
            )
            return [e.tolist() for e in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return None


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Get the singleton embedding service instance."""
    return EmbeddingService()
