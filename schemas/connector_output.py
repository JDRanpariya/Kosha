# Changed url: HttpUrl → str to support email:// and other non-HTTP schemes

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ConnectorOutput(BaseModel):
    title: str
    url: str          # str instead of HttpUrl — email connectors use non-HTTP schemes
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = {}
