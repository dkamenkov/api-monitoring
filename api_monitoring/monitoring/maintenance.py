import asyncio
from typing import Tuple, Optional

import aiohttp

from api_monitoring.config import settings
from api_monitoring.utils.logging import get_logger

logger = get_logger(__name__)


class MaintenanceChecker:
    """Checks if an API endpoint is in maintenance mode."""

    def __init__(self, endpoint_url: str, timeout: int = 10):
        """
        Initialize the maintenance checker.

        Args:
            endpoint_url: The endpoint URL to check
            timeout: Timeout for the request in seconds
        """
        self.endpoint_url = endpoint_url
        self.timeout = timeout

    async def is_on_maintenance(self) -> Tuple[bool, Optional[str]]:
        """
        Check if the API is in maintenance mode.

        Returns:
            A tuple of (is_maintenance, error_message) where is_maintenance is a boolean
            indicating if the API is in maintenance mode, and error_message is an optional
            error message if an error occurred during the check.
        """
        logger.info(f"Checking if API {self.endpoint_url} is on maintenance...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.endpoint_url, 
                    timeout=self.timeout,
                    allow_redirects=True
                ) as response:
                    # Check if the response contains the maintenance indicator
                    text = await response.text()

                    if "OnMaintenance" in text:
                        logger.info("API is on maintenance.")
                        return True, None

                    logger.info("API is not on maintenance.")
                    return False, None

        except asyncio.TimeoutError:
            error_msg = f"Timeout after waiting for {self.timeout} seconds."
            logger.error(error_msg)
            return False, error_msg

        except aiohttp.ClientConnectorError as e:
            error_msg = f"Connection error checking maintenance status: {e}"
            logger.error(error_msg)
            return False, error_msg

        except aiohttp.ClientResponseError as e:
            error_msg = f"Response error checking maintenance status: {e.status} - {e.message}"
            logger.error(error_msg)
            return False, error_msg

        except aiohttp.ClientError as e:
            error_msg = f"HTTP client error checking maintenance status: {e}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error checking maintenance status: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg


# Create a default maintenance checker instance
maintenance_checker = MaintenanceChecker(
    endpoint_url=settings.endpoint_url,
    timeout=settings.maintenance_check_timeout,
)
