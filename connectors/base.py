from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, ValidationError
import logging


class ConnectorConfig(BaseModel):
    """Base configuration — extend in every subclass."""
    max_results: int = 50

    model_config = {"extra": "allow"}   # tolerate unknown keys gracefully


class BaseConnector(ABC):
    """
    Abstract base for all content connectors.

    Subclasses must:
      1. Set ConfigModel to a ConnectorConfig subclass.
      2. Implement fetch() → list[ConnectorOutput].

    Optional:
      - Set source_type (str) for self-identification / logging.

    """

    ConfigModel: type[ConnectorConfig] = ConnectorConfig
    source_type: str = "unknown"

    def __init__(self, config: dict[str, Any]) -> None:
        try:
            self.config = self.ConfigModel(**config)
        except ValidationError as exc:
            raise ValueError(
                f"Invalid config for {self.__class__.__name__}:\n{exc}"
            ) from exc

        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    @abstractmethod
    def fetch(self) -> list:
        """Fetch items and return as list[ConnectorOutput]."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source_type={self.source_type!r})"
