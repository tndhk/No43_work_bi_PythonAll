"""Tests for logging configuration."""
import pytest
import structlog
from src.core.logging import setup_logging


def test_setup_logging_completes_successfully():
    """Test: setup_logging() completes without exceptions."""
    # Given: Logging not yet configured (or reset state)
    
    # When: Setting up logging
    # Then: No exception is raised
    setup_logging()


def test_setup_logging_configures_structlog():
    """Test: setup_logging() configures structlog."""
    # Given: Logging setup
    setup_logging()
    
    # When: Getting logger
    logger = structlog.get_logger()
    
    # Then: Logger is configured
    assert logger is not None
    
    # Then: Logger can be used without errors
    logger.info("test message")
