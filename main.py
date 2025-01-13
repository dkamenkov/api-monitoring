import boto3
import botocore
from dotenv import load_dotenv
from pathlib import Path
import os
import subprocess
import logging
import requests
from datetime import datetime
import concurrent.futures
import html
import time

# Initialize logging and load environment variables
logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class ApiChecker:
    def __init__(self) -> None:
        self.alert_sent: bool = False
        self.mtr_url: str = os.getenv("ENDPOINT_URL")
        self.endpoint_url: str = f"https://{self.mtr_url}"
        self.TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
        self.TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")

    def get_external_ip(self) -> str:
        """Retrieve the external IP address of the current machine."""
        logging.info("Retrieving external IP...")
        try:
            response = requests.get("https://httpbin.org/ip", timeout=5)
            ip = response.json()["origin"]
            logging.info(f"Successfully retrieved external IP: {ip}")
            return ip
        except Exception as e:
            logging.warning(f"Failed to retrieve IP from external service: {e}")
            logging.info("Falling back to EC2 metadata...")
            try:
                result = subprocess.run(
                    ["curl", "-s", "http://169.254.169.254/latest/meta-data/public-ipv4"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                )
                ip = result.stdout.strip()
                if ip:
                    logging.info(f"Successfully retrieved IP from EC2 metadata: {ip}")
                    return ip
                else:
                    logging.error("No IP returned from EC2 metadata.")
                    return "Unknown IP"
            except subprocess.CalledProcessError as e:
                logging.error(f"Error retrieving IP from EC2 metadata: {e}")
                return "Unknown IP"

    def is_on_maintenance(self, endpoint: str, timeout_seconds: int = 10) -> bool:
        """Determine if the API is on maintenance mode by checking for 'OnMaintenance' in the response."""
        logging.info("Checking if API is on maintenance...")
        try:
            response = requests.get(endpoint, timeout=timeout_seconds)
            if "OnMaintenance" in response.text:
                logging.info("API is on maintenance.")
                return True
            logging.info("API is not on maintenance.")
            return False
        except requests.exceptions.Timeout:
            logging.error(f"Timeout after waiting for {timeout_seconds} seconds.")
            if not self.alert_sent:
                mtr_output = self.run_mtr(self.mtr_url)
                self.send_alert(
                    self.mtr_url,
                    mtr_output if mtr_output else "MTR failed to execute",
                    "Timeout during maintenance check",
                )
            return False
        except Exception as e:
            logging.error(f"Error checking maintenance status: {e}")
            return False

    def telegram_sender(self, text: str) -> None:
        """Send a specified message to a Telegram chat."""
        logging.info("Sending message to Telegram...")
        url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": self.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}

        try:
            response = requests.post(url, data=payload, timeout=5)
            if response.status_code != 200:
                logging.error(f"Failed to send message to Telegram: {response.content}")
        except Exception as e:
            logging.error(f"Error when trying to send message to Telegram: {e}")

    def send_alert(self, mtr_url: str, mtr_output: str, error_message: str = None) -> None:
        """Send an alert to Telegram regarding an issue with the API."""
        logging.info("Compiling alert message...")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        source_ip = self.get_external_ip()

        # Escape received values for safety
        mtr_output = f"<pre>{html.escape(mtr_output)}</pre>"
        error_message = f"<code>{html.escape(error_message)}</code>"

        alert_message = f"""
<b>🚨 Issue detected with API {mtr_url} 🚨</b>
<b>Timestamp:</b> {now}
<b>Source IP:</b> {source_ip}
<b>Error:</b> {error_message}
<b>Trace to {mtr_url}:</b>
{mtr_output}
"""
        self.telegram_sender(alert_message)
        self.alert_sent = True
        logging.info("Alert sent and alert_sent set to True.")

    def check_api(self) -> (bool, str):
        """Attempt to access the API and return its status and any associated error message."""
        logging.info("Checking API status...")
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        # Set timeouts for the session
        config = botocore.config.Config(connect_timeout=5, read_timeout=10)

        client = session.client("ec2", endpoint_url=self.endpoint_url, config=config)

        try:
            logging.info("Calling describe_availability_zones()...")
            response = client.describe_availability_zones()
            logging.info("describe_availability_zones() call completed.")
            return True, ""
        except botocore.exceptions.EndpointConnectionError as e:
            logging.error(f"Cannot connect to the endpoint: {e}")
            return False, f"Cannot connect to the endpoint: {e}"
        except botocore.exceptions.PartialCredentialsError as e:
            logging.error(f"Incomplete credentials provided: {e}")
            return False, f"Incomplete credentials provided: {e}"
        except botocore.exceptions.SSLError as e:
            logging.error(f"SSL/TLS error occurred: {e}")
            return False, f"SSL/TLS error occurred: {e}"
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logging.error(f"ClientError occurred: {error_code} - {error_message}")
            return False, f"ClientError occurred: {error_code} - {error_message}"
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return False, f"Unexpected error: {e}"

    def run_mtr(self, target: str) -> str:
        """Execute MTR to get a network trace to the specified target."""
        logging.info(f"Running MTR for target: {target}")
        try:
            result = subprocess.run(
                ["mtr", "--report", "--report-cycles", "1", "-4", "--no-dns", target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"MTR error: {e}")
            logging.error(f"stderr: {e.stderr}")
            return ""
        except Exception as e:
            logging.error(f"General error running MTR: {e}")
            return ""

    def run(self) -> None:
        """Main function to check the API and send alerts."""
        logging.info("Initializing main run sequence...")

        while True:  # бесконечный цикл
            if self.is_on_maintenance(self.endpoint_url):
                logging.info("The service is on maintenance. Skipping checks.")
                time.sleep(60)
                continue

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.check_api)

                try:
                    success, error_message = future.result(timeout=15)

                    if not success:
                        if not self.alert_sent:
                            mtr_output = self.run_mtr(self.mtr_url)
                            if mtr_output:
                                self.send_alert(self.mtr_url, mtr_output, error_message)
                            else:
                                logging.error("Failed to get MTR trace.")
                                self.send_alert(self.mtr_url, "MTR failed to execute", "MTR error: Unable to resolve host")
                        else:
                            logging.info("API check failed, but alert was already sent.")
                    else:
                        if self.alert_sent:
                            self.telegram_sender(f"🟢 Issue with API {self.mtr_url} resolved!")
                            self.alert_sent = False
                            logging.info("API issue resolved and alert_sent set to False.")
                        else:
                            logging.info("API check succeeded and no previous alert was sent.")

                except concurrent.futures.TimeoutError:
                    logging.error("API check timed out")
                    if not self.alert_sent:
                        mtr_output = self.run_mtr(self.mtr_url)
                        if mtr_output:
                            self.send_alert(self.mtr_url, mtr_output, "API check timed out")
                        else:
                            logging.error("Failed to get MTR trace.")
                            self.send_alert(self.mtr_url, "MTR failed to execute", "Timeout and MTR error")
                    else:
                        logging.info("API check timed out, but alert was already sent.")

            time.sleep(60)


if __name__ == "__main__":
    checker = ApiChecker()
    checker.run()
