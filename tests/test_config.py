import os
import unittest
from unittest.mock import patch

from api_monitoring.config import Settings


class TestSettings(unittest.TestCase):
    """Test the Settings class from the config module."""

    def setUp(self):
        """Set up test environment variables."""
        self.env_vars = {
            "ENDPOINT_URL": "test-api.example.com",
            "AWS_ACCESS_KEY_ID": "test-access-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret-key",
            "AWS_DEFAULT_REGION": "us-west-2",
            "TELEGRAM_BOT_TOKEN": "test-bot-token",
            "TELEGRAM_CHAT_ID": "test-chat-id",
            "CHECK_INTERVAL": "30",
            "API_TIMEOUT": "10",
            "MAINTENANCE_CHECK_TIMEOUT": "5",
            "LOG_LEVEL": "DEBUG",
        }

    @patch.dict(os.environ, {}, clear=True)
    def test_required_settings(self):
        """Test that required settings raise an error when missing."""

        # Create a Settings class that doesn't load from .env file
        class TestSettings(Settings):
            model_config = Settings.model_config.copy()
            model_config.update({"env_file": None})

        with self.assertRaises(Exception):
            TestSettings()

    @patch.dict(
        os.environ,
        {
            "ENDPOINT_URL": "test-api.example.com",
            "AWS_ACCESS_KEY_ID": "test-access-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret-key",
            "TELEGRAM_BOT_TOKEN": "test-bot-token",
            "TELEGRAM_CHAT_ID": "test-chat-id",
        },
    )
    def test_minimal_settings(self):
        """Test that minimal required settings work."""

        # Create a Settings class that doesn't load from .env file
        class TestSettings(Settings):
            model_config = Settings.model_config.copy()
            model_config.update({"env_file": None})

        settings = TestSettings()
        self.assertEqual(settings.endpoint_url, "https://test-api.example.com")
        self.assertEqual(settings.aws_access_key_id, "test-access-key")
        self.assertEqual(settings.aws_secret_access_key, "test-secret-key")
        self.assertEqual(settings.telegram_bot_token, "test-bot-token")
        self.assertEqual(settings.telegram_chat_id, "test-chat-id")
        # Check defaults
        self.assertEqual(settings.aws_default_region, "us-east-1")
        self.assertEqual(settings.check_interval, 60)
        self.assertEqual(settings.api_timeout, 15)
        self.assertEqual(settings.maintenance_check_timeout, 10)
        self.assertEqual(settings.log_level, "INFO")
        self.assertEqual(settings.log_file, "logs.log")
        self.assertIsNone(settings.alert_comment)
        # Check new failure threshold defaults
        self.assertEqual(settings.maintenance_failure_threshold, 1)
        self.assertEqual(settings.api_failure_threshold, 1)

    @patch.dict(
        os.environ,
        {
            "ENDPOINT_URL": "http://test-api.example.com",
            "AWS_ACCESS_KEY_ID": "test-access-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret-key",
            "AWS_DEFAULT_REGION": "us-west-2",
            "TELEGRAM_BOT_TOKEN": "test-bot-token",
            "TELEGRAM_CHAT_ID": "test-chat-id",
            "CHECK_INTERVAL": "30",
            "API_TIMEOUT": "10",
            "MAINTENANCE_CHECK_TIMEOUT": "5",
            "LOG_LEVEL": "DEBUG",
            "LOG_FILE": "custom.log",
            "ALERT_COMMENT": "Test alert comment",
            "MAINTENANCE_FAILURE_THRESHOLD": "3",
            "API_FAILURE_THRESHOLD": "2",
        },
    )
    def test_full_settings(self):
        """Test that all settings are loaded correctly."""
        settings = Settings()
        self.assertEqual(settings.endpoint_url, "http://test-api.example.com")
        self.assertEqual(settings.aws_access_key_id, "test-access-key")
        self.assertEqual(settings.aws_secret_access_key, "test-secret-key")
        self.assertEqual(settings.aws_default_region, "us-west-2")
        self.assertEqual(settings.telegram_bot_token, "test-bot-token")
        self.assertEqual(settings.telegram_chat_id, "test-chat-id")
        self.assertEqual(settings.check_interval, 30)
        self.assertEqual(settings.api_timeout, 10)
        self.assertEqual(settings.maintenance_check_timeout, 5)
        self.assertEqual(settings.log_level, "DEBUG")
        self.assertEqual(settings.log_file, "custom.log")
        self.assertEqual(settings.alert_comment, "Test alert comment")
        # Check new failure threshold settings
        self.assertEqual(settings.maintenance_failure_threshold, 3)
        self.assertEqual(settings.api_failure_threshold, 2)

    @patch.dict(
        os.environ,
        {
            "ENDPOINT_URL": "test-api.example.com",  # No protocol
            "AWS_ACCESS_KEY_ID": "test-access-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret-key",
            "TELEGRAM_BOT_TOKEN": "test-bot-token",
            "TELEGRAM_CHAT_ID": "test-chat-id",
        },
    )
    def test_endpoint_url_validator(self):
        """Test that the endpoint_url validator adds https:// if missing."""
        settings = Settings()
        self.assertEqual(settings.endpoint_url, "https://test-api.example.com")


if __name__ == "__main__":
    unittest.main()
