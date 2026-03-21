# backend/core/logging.py

"""
Structured logging with correlation IDs.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

# Context variable for correlation ID (thread-safe)

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Get current correlation ID or generate a new one."""
    cid = correlation_id_ctx.get()
    if not cid:
        cid = str(uuid.uuid4())[:8]
        correlation_id_ctx.set(cid)
    return cid


def set_correlation_id(cid: str | None = None) -> str:
    """Set correlation ID for current context."""
    cid = cid or str(uuid.uuid4())[:8]
    correlation_id_ctx.set(cid)
    return cid


class CorrelationIdFilter(logging.Filter):
    """Inject correlation ID into log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


class StructuredFormatter(logging.Formatter):
    """JSON-like structured log format for production."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "correlation_id": getattr(record, "correlation_id", ""),
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "correlation_id", "message",
            ):
                log_data[key] = value
        
        # Simple key=value format for readability
        parts = [f"{k}={v}" for k, v in log_data.items() if v]
        return " | ".join(parts)


def setup_logging(level: str = "INFO", structured: bool = False) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        structured: Use structured format (for production)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(CorrelationIdFilter())
    
    if structured:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | [%(correlation_id)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
    
    root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)
