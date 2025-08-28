import asyncio
from typing import Optional, Tuple

from api_monitoring.alerting.telegram import telegram_alerter
from api_monitoring.clients.aws_client import aws_client
from api_monitoring.config import settings
from api_monitoring.monitoring.maintenance import maintenance_checker
from api_monitoring.utils.logging import get_logger
from api_monitoring.utils.network import run_mtr

logger = get_logger(__name__)


class ApiMonitor:
    """
    Main API monitoring class that orchestrates the monitoring process.

    This class coordinates checking if the API is in maintenance mode,
    checking API availability, and sending alerts when issues are detected.
    """

    def __init__(
        self,
        check_interval: int = 60,
        api_timeout: int = 15,
        target_hostname: Optional[str] = None,
    ):
        """
        Initialize the API monitor.

        Args:
            check_interval: Interval between API checks in seconds
            api_timeout: Timeout for API requests in seconds
            target_hostname: The hostname to use for MTR traces (defaults to endpoint URL hostname)
        """
        self.check_interval = check_interval
        self.api_timeout = api_timeout

        # Extract hostname from endpoint URL if not provided
        if target_hostname is None:
            # Remove protocol prefix if present
            url = settings.endpoint_url
            if "://" in url:
                url = url.split("://")[1]
            # Extract hostname (remove path and query parameters)
            self.target_hostname = url.split("/")[0]
        else:
            self.target_hostname = target_hostname

        # Failure counters for threshold-based alerting
        self.maintenance_failure_count = 0
        self.api_failure_count = 0

        logger.info(
            f"Initialized API monitor for {self.target_hostname} with check interval {check_interval}s"
        )
        logger.info(
            f"Failure thresholds: maintenance={settings.maintenance_failure_threshold}, "
            f"api={settings.api_failure_threshold}"
        )

    async def check_api_with_timeout(self) -> Tuple[bool, Optional[str]]:
        """
        Check API availability with a timeout.

        Returns:
            A tuple of (success, error_message) where success is a boolean indicating if the
            API is available, and error_message is an optional error message if not available.
        """
        try:
            # Use asyncio.wait_for to implement timeout
            return await asyncio.wait_for(
                aws_client.check_api_availability(), timeout=self.api_timeout
            )
        except asyncio.TimeoutError:
            error_msg = f"API check timed out after {self.api_timeout} seconds"
            logger.error(error_msg)
            return False, error_msg

    def should_send_maintenance_alert(self) -> bool:
        """
        Check if a maintenance failure alert should be sent based on the failure threshold.

        Returns:
            True if an alert should be sent, False otherwise.
        """
        self.maintenance_failure_count += 1
        logger.info(
            f"Maintenance failure count: {self.maintenance_failure_count}/{settings.maintenance_failure_threshold}"
        )

        if self.maintenance_failure_count >= settings.maintenance_failure_threshold:
            return True
        return False

    def should_send_api_alert(self) -> bool:
        """
        Check if an API failure alert should be sent based on the failure threshold.

        Returns:
            True if an alert should be sent, False otherwise.
        """
        self.api_failure_count += 1
        logger.info(
            f"API failure count: {self.api_failure_count}/{settings.api_failure_threshold}"
        )

        if self.api_failure_count >= settings.api_failure_threshold:
            return True
        return False

    def reset_failure_counters(self) -> None:
        """Reset all failure counters when checks succeed."""
        if self.maintenance_failure_count > 0 or self.api_failure_count > 0:
            logger.info("Resetting failure counters after successful checks")
            self.maintenance_failure_count = 0
            self.api_failure_count = 0

    async def handle_api_failure(
        self, error_message: str, comment: Optional[str] = None
    ) -> None:
        """
        Handle API failure by running MTR and sending an alert.

        Args:
            error_message: The error message from the API check
            comment: Optional comment to include in the alert
        """
        logger.info("Handling API failure...")

        # Only send an alert if one hasn't been sent already
        if not telegram_alerter.alert_sent:
            # Run MTR to trace the network path
            success, mtr_output = await run_mtr(self.target_hostname)

            if success:
                # Send alert with MTR output
                await telegram_alerter.send_alert(
                    self.target_hostname, mtr_output, error_message, comment
                )
            else:
                # Send alert without MTR output
                await telegram_alerter.send_alert(
                    self.target_hostname,
                    "MTR failed to execute",
                    f"{error_message} (MTR error: {mtr_output})",
                    comment,
                )
        else:
            logger.info("API check failed, but alert was already sent.")

    async def run_once(self) -> bool:
        """
        Run a single monitoring cycle.

        Returns:
            True if check was successful or maintenance mode, False if there was a failure
            that hasn't reached the threshold (indicating immediate retry should happen).
        """
        logger.info("Starting monitoring cycle...")

        # Check if the API is in maintenance mode
        is_maintenance, maintenance_error = (
            await maintenance_checker.is_on_maintenance()
        )

        if is_maintenance:
            logger.info("The service is on maintenance. Skipping further checks.")
            # Reset failure counters since maintenance is expected
            self.reset_failure_counters()
            return True

        if maintenance_error:
            # Handle maintenance check failure with threshold
            if self.should_send_maintenance_alert():
                await self.handle_api_failure(
                    f"Maintenance check failed: {maintenance_error}",
                    settings.alert_comment,
                )
                return True  # Alert sent, use normal interval
            else:
                logger.warning(
                    f"Maintenance check failed ({self.maintenance_failure_count}/{settings.maintenance_failure_threshold}): {maintenance_error}"
                )
                return False  # Failure without alert, retry immediately

        # Check API availability
        success, error_message = await self.check_api_with_timeout()

        if not success:
            # API is not available - check threshold before alerting
            if self.should_send_api_alert():
                await self.handle_api_failure(
                    error_message or "Unknown error", settings.alert_comment
                )
                return True  # Alert sent, use normal interval
            else:
                logger.warning(
                    f"API check failed ({self.api_failure_count}/{settings.api_failure_threshold}): {error_message}"
                )
                return False  # Failure without alert, retry immediately
        else:
            # API is available
            logger.info("API check succeeded.")

            # Reset failure counters on successful check
            self.reset_failure_counters()

            # If an alert was previously sent, send a resolution message
            if telegram_alerter.alert_sent:
                await telegram_alerter.send_resolution(self.target_hostname)

            return True  # Success, use normal interval

    async def run(self) -> None:
        """
        Run the monitoring process continuously.

        This method runs in an infinite loop, checking the API at regular intervals.
        """
        logger.info(f"Starting continuous monitoring for {self.target_hostname}...")

        while True:
            try:
                should_wait = await self.run_once()
            except asyncio.CancelledError:
                logger.info("Monitoring task was cancelled")
                break
            except Exception as e:
                logger.error(
                    f"Unexpected error in monitoring cycle: {e}", exc_info=True
                )
                # Consider sending an alert about the monitoring system itself
                await self.handle_api_failure(
                    f"Monitoring system error: {str(e)}", settings.alert_comment
                )
                should_wait = True  # Wait normal interval after system errors

            # Wait for the next check interval only if check was successful or alert was sent
            if should_wait:
                logger.info(
                    f"Waiting {self.check_interval} seconds until next check..."
                )
                await asyncio.sleep(self.check_interval)
            else:
                logger.info("Retrying immediately due to failure below threshold...")
                # Small delay to prevent tight loop in case of persistent issues
                await asyncio.sleep(1)


# Create a default API monitor instance
api_monitor = ApiMonitor(
    check_interval=settings.check_interval,
    api_timeout=settings.api_timeout,
)
