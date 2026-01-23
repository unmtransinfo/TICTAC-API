"""Exception handling utilities for database errors."""

import logging

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def handle_database_error(error: Exception, endpoint_name: str) -> HTTPException:
    """
    Handle database errors and return appropriate HTTP exception.

    Args:
        error: The exception that occurred
        endpoint_name: Name of the endpoint where error occurred (for logging)

    Returns:
        HTTPException: Appropriate HTTP exception with status code and detail
    """
    if isinstance(error, SQLAlchemyError):
        logger.error(
            f"Database error in {endpoint_name}: {type(error).__name__}: {error}",
            exc_info=True,
        )
        return HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable. Please try again later.",
        )
    else:
        logger.error(
            f"Unexpected error in {endpoint_name}: {type(error).__name__}: {error}",
            exc_info=True,
        )
        return HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later.",
        )
