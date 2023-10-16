import boto3
import botocore
from dotenv import load_dotenv
import os
import subprocess
import logging
import requests
from datetime import datetime
import concurrent.futures

load_dotenv()
logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_maintanace():
    ''''''

class ApiChecker:
    def __init__(self):
        self.alert_sent = False
        self.mtr_url = os.getenv('ENDPOINT_URL')
        self.endpoint_url = "https://" + self.mtr_url
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    def get_external_ip(self):
        try:
            response = requests.get("https://httpbin.org/ip", timeout=5)  # добавлен таймаут
            ip = response.json()["origin"]
            return ip
        except Exception as e:
            logging.error(f"Error getting external IP: {str(e)}")
            return "Unknown IP"
        
    def telegram_sender(self, text):
        url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"

        payload = {
            'chat_id': self.TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML'
        }

        try:
            response = requests.post(url, data=payload, timeout=5)  # добавлен таймаут
            if response.status_code != 200:
                logging.error(f"Failed to send message to Telegram: {response.content}")
        except Exception as e:
            logging.error(f"An error occurred when trying to send message to Telegram: {str(e)}")
            # Дополнительные действия при ошибке отправки уведомления...

    def send_alert(self, mtr_url, mtr_output, error_message=None):
        logging.info("Sending alert...")  # добавлено логгирование
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Получение IP-адреса текущего хоста

        source_ip = self.get_external_ip()  # убрано дублирование

        # Формирование сообщения
        alert_message = f"""
<b>🚨 Обнаружена проблема с работоспособностью API {mtr_url} 🚨</b>
<b>Дата/время фиксации проблемы:</b> {now}
<b>Адрес источника обращения к API:</b> {source_ip}
<b>Ссылка на регламент:</b> <a href='[Ваша ссылка здесь]'>Перейти к регламенту</a>
<b>Ошибка:</b> {error_message}
<b>Трассировка до {mtr_url}:</b>
<pre>
{mtr_output}
</pre>
"""
        self.telegram_sender(alert_message)

    def check_api(self):
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )
        # Установка таймаутов для сессии
        config = botocore.config.Config(
            connect_timeout=5,  # Установка таймаута подключения
            read_timeout=10,    # Установка таймаута чтения
        )

        client = session.client(
            'ec2',
            endpoint_url=self.endpoint_url,
            config=config,
        )
        error = None
        try:
            logging.info("Calling describe_availability_zones()...")  # Добавлено логгирование
            response = client.describe_availability_zones()
            logging.info("describe_availability_zones() call completed.")
            return True, None
        except botocore.exceptions.EndpointConnectionError as e:
            logging.error(f"Cannot connect to the endpoint: {str(e)}")
            error = f"Cannot connect to the endpoint: {str(e)}"
        except botocore.exceptions.PartialCredentialsError as e:
            logging.error(f"Incomplete credentials provided: {str(e)}")
            error = f"Incomplete credentials provided: {str(e)}"
        except botocore.exceptions.SSLError as e:
            logging.error(f"SSL/TLS error occurred: {str(e)}")
            error = f"SSL/TLS error occurred: {str(e)}"
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logging.error(f"ClientError occurred: {error_code} - {error_message}")
            error = f"ClientError occurred: {error_code} - {error_message}"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            error = f"An unexpected error occurred: {str(e)}"

        return False, error

    def run_mtr(self, target):
        target = self.mtr_url
        try:
            result = subprocess.run(["mtr", "--report", "--report-cycles", "1", "-4", "--no-dns", target],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"An error occurred: {str(e)}")
            logging.error(f"stderr: {e.stderr}")
            return None

    def run(self):
        logging.info("Starting main...")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.check_api)
            try:
                success, error_message = future.result(timeout=15)

                if not success:
                    if not self.alert_sent:
                        mtr_output = self.run_mtr(self.mtr_url)
                        if mtr_output:
                            self.send_alert(self.mtr_url, mtr_output, error_message)
                            self.alert_sent = True
                        else:
                            logging.error("Failed to get MTR trace.")
                else:
                    if self.alert_sent:
                        self.telegram_sender(f"🟢 Проблема с API {self.mtr_url} решена!")
                        self.alert_sent = False

            except concurrent.futures.TimeoutError:
                logging.error("API check timed out")
                mtr_output = self.run_mtr(self.mtr_url)
                if mtr_output:
                    self.send_alert(self.mtr_url, mtr_output, "API check timed out")
                else:
                    logging.error("Failed to get MTR trace.")


if __name__ == "__main__":
    checker = ApiChecker()
    checker.run()
