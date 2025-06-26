import asyncio
from typing import Optional, Tuple

import aiobotocore.session
from aiobotocore.config import AioConfig
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    PartialCredentialsError,
    SSLError,
)

from api_monitoring.config import settings
from api_monitoring.utils.logging import get_logger

logger = get_logger(__name__)


class AWSClient:
    """Asynchronous AWS API client for interacting with AWS-compatible APIs."""

    def __init__(
        self,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        connect_timeout: int = 5,
        read_timeout: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize the AWS client.

        Args:
            endpoint_url: The endpoint URL for the AWS-compatible API
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.config = AioConfig(
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            retries={"max_attempts": max_retries},
        )
        self.session = aiobotocore.session.get_session()

    async def check_api_availability(self) -> Tuple[bool, Optional[str]]:
        """
        Check if the AWS-compatible API is available.

        Returns:
            A tuple of (success, error_message) where success is a boolean indicating if the
            API is available, and error_message is an optional error message if not available.
        """
        logger.info(f"Checking API availability for {self.endpoint_url}")

        try:
            async with self.session.create_client(
                "ec2",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
                config=self.config,
            ) as client:
                logger.info("Calling describe_availability_zones()...")
                response = await client.describe_availability_zones()
                logger.info("describe_availability_zones() call completed successfully")
                return True, None

        except EndpointConnectionError as e:
            error_msg = f"Cannot connect to the endpoint: {e}"
            logger.error(error_msg)
            return False, error_msg

        except PartialCredentialsError as e:
            error_msg = f"Incomplete credentials provided: {e}"
            logger.error(error_msg)
            return False, error_msg

        except SSLError as e:
            error_msg = f"SSL/TLS error occurred: {e}"
            logger.error(error_msg)
            return False, error_msg

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            error_msg = f"ClientError occurred: {error_code} - {error_message}"
            logger.error(error_msg)
            return False, error_msg

        except asyncio.TimeoutError:
            error_msg = "API request timed out"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


# Create a default AWS client instance
aws_client = AWSClient(
    endpoint_url=settings.endpoint_url,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_default_region,
)
