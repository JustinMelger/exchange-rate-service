import logging
from functools import wraps
from typing import Callable

from fastapi import HTTPException

logger = logging.getLogger(__name__)


class IngestServiceError(HTTPException):
    """Base FastAPI exception for the ingest service."""

    def __init__(self, *, detail: str, status_code: int) -> None:
        super().__init__(status_code=status_code, detail=detail)


def ingest_error_handler(
    message: str = "An unexpected error occurred while ingesting exchange rates", status_code: int = 500
) -> Callable:
    """Decorator that converts any uncaught exception into an IngestServiceError."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                logger.error("Error while ingesting exchange rates", exc_info=exc)
                raise IngestServiceError(detail=message, status_code=status_code)

        return wrapper

    return decorator
