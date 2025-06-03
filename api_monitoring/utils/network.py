import asyncio
import subprocess
from typing import Optional, Tuple

import aiohttp

from api_monitoring.utils.logging import get_logger

logger = get_logger(__name__)


async def get_external_ip() -> str:
    """
    Asynchronously retrieve the external IP address of the current machine.

    Returns:
        The external IP address as a string, or "Unknown IP" if it cannot be determined.
    """
    logger.info("Retrieving external IP...")

    # Try using httpbin.org first
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://httpbin.org/ip", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    ip = data.get("origin", "")
                    if ip:
                        logger.info(f"Successfully retrieved external IP: {ip}")
                        return ip
                logger.warning(f"Failed to retrieve IP from httpbin.org: HTTP {response.status}")
    except asyncio.TimeoutError:
        logger.warning("Timeout retrieving IP from httpbin.org")
    except aiohttp.ClientConnectorError as e:
        logger.warning(f"Connection error retrieving IP from httpbin.org: {e}")
    except aiohttp.ClientResponseError as e:
        logger.warning(f"Response error retrieving IP from httpbin.org: {e.status} - {e.message}")
    except aiohttp.ClientError as e:
        logger.warning(f"HTTP client error retrieving IP from httpbin.org: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error retrieving IP from external service: {e}", exc_info=True)

    # Fall back to EC2 metadata
    logger.info("Falling back to EC2 metadata...")
    try:
        # Use asyncio to run the subprocess command
        proc = await asyncio.create_subprocess_exec(
            "curl", "-s", "http://169.254.169.254/latest/meta-data/public-ipv4",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            ip = stdout.decode().strip()
            if ip:
                logger.info(f"Successfully retrieved IP from EC2 metadata: {ip}")
                return ip
            else:
                logger.error("No IP returned from EC2 metadata.")
        else:
            logger.error(f"Error retrieving IP from EC2 metadata: {stderr.decode()}")
    except Exception as e:
        logger.error(f"Exception retrieving IP from EC2 metadata: {e}")

    return "Unknown IP"


async def run_mtr(target: str) -> Tuple[bool, str]:
    """
    Asynchronously execute MTR to get a network trace to the specified target.

    Args:
        target: The hostname or IP address to trace

    Returns:
        A tuple of (success, output) where success is a boolean indicating if the
        command was successful, and output is the command output or error message.
    """
    logger.info(f"Running MTR for target: {target}")

    try:
        # Use asyncio to run the subprocess command
        proc = await asyncio.create_subprocess_exec(
            "mtr", "--report", "--report-cycles", "1", "-4", "--no-dns", target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            output = stdout.decode()
            logger.info("MTR trace successfully retrieved")
            return True, output
        else:
            error = stderr.decode()
            logger.error(f"MTR error: {error}")
            return False, f"MTR command failed: {error}"
    except Exception as e:
        logger.error(f"General error running MTR: {e}")
        return False, f"Exception running MTR: {str(e)}"


async def is_command_available(command: str) -> bool:
    """
    Check if a command is available in the system.

    Args:
        command: The command to check

    Returns:
        True if the command is available, False otherwise
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            "which", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, _ = await proc.communicate()
        return proc.returncode == 0
    except Exception:
        return False


def is_command_available_sync(command: str) -> bool:
    """
    Synchronous version of is_command_available.

    Args:
        command: The command to check

    Returns:
        True if the command is available, False otherwise
    """
    try:
        subprocess.run(
            ["which", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
