import asyncio
import html
from datetime import datetime
from typing import Optional

import aiohttp

from api_monitoring.config import settings
from api_monitoring.utils.logging import get_logger
from api_monitoring.utils.network import get_external_ip

logger = get_logger(__name__)


class TelegramAlerter:
    """Sends alerts to Telegram."""

    def __init__(self, bot_token: str, chat_id: str, timeout: int = 10):
        """
        Initialize the Telegram alerter.

        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
            timeout: Timeout for Telegram API requests in seconds
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.timeout = timeout
        self.alert_sent = False

    async def send_message(self, text: str) -> bool:
        """
        Send a message to Telegram.

        Args:
            text: The message text to send

        Returns:
            True if the message was sent successfully, False otherwise
        """
        logger.info("Sending message to Telegram...")

        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status == 200:
                        logger.info("Message sent to Telegram successfully")
                        return True
                    else:
                        response_text = await response.text()
                        logger.error(
                            f"Failed to send message to Telegram: {response.status} - {response_text}"
                        )
                        return False
        except asyncio.TimeoutError:
            logger.error(
                f"Timeout sending message to Telegram after {self.timeout} seconds"
            )
            return False
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error sending message to Telegram: {e}")
            return False
        except aiohttp.ClientResponseError as e:
            logger.error(
                f"Response error sending message to Telegram: {e.status} - {e.message}"
            )
            return False
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error sending message to Telegram: {e}")
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error sending message to Telegram: {e}", exc_info=True
            )
            return False

    async def send_alert(
        self,
        target: str,
        mtr_output: str,
        error_message: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> bool:
        """
        Send an alert about an API issue to Telegram.

        Args:
            target: The target API that has an issue
            mtr_output: The MTR trace output
            error_message: Optional error message describing the issue
            comment: Optional comment to include in the alert

        Returns:
            True if the alert was sent successfully, False otherwise
        """
        logger.info("Compiling alert message...")

        # Get current timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get source IP
        source_ip = await get_external_ip()

        # Escape received values for safety
        safe_mtr_output = (
            f"<pre>{html.escape(mtr_output)}</pre>"
            if mtr_output
            else "<pre>No MTR output available</pre>"
        )
        safe_error_message = (
            f"<code>{html.escape(error_message)}</code>"
            if error_message
            else "<code>Unknown error</code>"
        )
        safe_comment = f"<i>{html.escape(comment)}</i>" if comment else ""

        # Prepare comment section if provided
        comment_section = f"<b>Comment:</b> {safe_comment}\n" if comment else ""

        # Format the alert message
        alert_message = f"""
<b>🚨 Issue detected with API {target} 🚨</b>
<b>Timestamp:</b> {now}
<b>Source IP:</b> {source_ip}
<b>Error:</b> {safe_error_message}
{comment_section}<b>Trace to {target}:</b>
{safe_mtr_output}
"""

        # Send the message
        success = await self.send_message(alert_message)

        if success:
            self.alert_sent = True
            logger.info("Alert sent and alert_sent set to True")

        return success

    async def send_resolution(self, target: str) -> bool:
        """
        Send a resolution message when an API issue is resolved.

        Args:
            target: The target API that has been resolved

        Returns:
            True if the message was sent successfully, False otherwise
        """
        resolution_message = f"🟢 Issue with API {target} resolved!"

        success = await self.send_message(resolution_message)

        if success:
            self.alert_sent = False
            logger.info("Resolution message sent and alert_sent set to False")

        return success


# Create a default Telegram alerter instance
telegram_alerter = TelegramAlerter(
    bot_token=settings.telegram_bot_token,
    chat_id=settings.telegram_chat_id,
    timeout=settings.api_timeout,  # Use the same timeout as API requests
)
