#!/usr/bin/env python3
"""
API Monitoring Tool

This script monitors the availability of an AWS-compatible API and sends alerts
when issues are detected.
"""
import asyncio
import signal
import sys
from typing import Optional

from api_monitoring.config import settings
from api_monitoring.monitoring.monitor import api_monitor
from api_monitoring.utils.logging import logger
from api_monitoring.utils.network import is_command_available, is_command_available_sync


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""

    def handle_exit(sig: int, frame) -> None:
        """Handle exit signals."""
        logger.info(f"Received signal {sig}, shutting down...")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)


async def check_prerequisites() -> Optional[str]:
    """
    Check if all prerequisites are met.

    Returns:
        An error message if prerequisites are not met, None otherwise.
    """
    # Check if MTR is installed
    if not await is_command_available("mtr"):
        return "MTR is not installed. Please install it using your package manager."

    # Check if required environment variables are set
    required_vars = [
        "endpoint_url",
        "aws_access_key_id",
        "aws_secret_access_key",
        "telegram_bot_token",
        "telegram_chat_id",
    ]

    missing_vars = []
    for var in required_vars:
        try:
            value = getattr(settings, var)
            if not value:
                missing_vars.append(var)
        except Exception:
            missing_vars.append(var)

    if missing_vars:
        return f"Missing required environment variables: {', '.join(missing_vars)}"

    return None


async def main() -> None:
    """Main entry point for the application."""
    logger.info("Starting API Monitoring Tool...")

    # Check prerequisites
    error = await check_prerequisites()
    if error:
        logger.error(f"Prerequisite check failed: {error}")
        sys.exit(1)

    # Set up signal handlers
    setup_signal_handlers()

    # Log configuration
    logger.info(f"Monitoring endpoint: {settings.endpoint_url}")
    logger.info(f"Check interval: {settings.check_interval} seconds")
    logger.info(f"API timeout: {settings.api_timeout} seconds")

    try:
        # Start the monitoring process
        await api_monitor.run()
    except Exception as e:
        logger.error(f"Unhandled exception in main loop: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
