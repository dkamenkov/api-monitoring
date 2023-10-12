import boto3
import botocore
from dotenv import load_dotenv
import os
import subprocess
import logging
import requests
from datetime import datetime


load_dotenv()
endpoint_url = os.getenv('ENDPOINT_URL')
logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_external_ip():
    try:
        response = requests.get("https://httpbin.org/ip")
        ip = response.json()["origin"]
        return ip
    except Exception as e:
        logging.error(f"Error getting external IP: {str(e)}")
        return "Unknown IP"


def is_maintanace():
    ''''''

def telegram_sender(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            logging.error(f"Failed to send message to Telegram: {response.content}")
    except Exception as e:
        logging.error(f"An error occurred when trying to send message to Telegram: {str(e)}")


def send_alert(endpoint_url, mtr_output):
    # Получение текущего времени
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Получение IP-адреса текущего хоста
    source_ip = source_ip = get_external_ip()

    # Формирование сообщения
    alert_message = f"""
    🚨 Обнаружена проблема с работоспособностью API {endpoint_url} 🚨
    Дата/время фиксации проблемы: {now}
    Адрес источника обращения к API: {source_ip}
    Ссылка на регламент: [Добавьте ссылку здесь]
    Трассировка до {endpoint_url}:
    ```
    {mtr_output}
    ```
    """
    telegram_sender(alert_message)


def check_api():
    client = boto3.client(
        'ec2',
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
        endpoint_url = endpoint_url,
    )
    try:
        response = client.describe_availability_zones()
        print('Availability Zones:', response['AvailabilityZones'])
    except botocore.exceptions.EndpointConnectionError as e:
        logging.error(f"Cannot connect to the endpoint: {str(e)}")

    except botocore.exceptions.PartialCredentialsError as e:
        logging.error(f"Incomplete credentials provided: {str(e)}")

    except botocore.exceptions.SSLError as e:
        logging.error(f"SSL/TLS error occurred: {str(e)}")

    except botocore.exceptions.ClientError as e:
        # Дополнительную информацию о ошибке можно извлечь из объекта исключения
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logging.error(f"ClientError occurred: {error_code} - {error_message}")

    except Exception as e:
        # Обработка всех остальных исключений
        logging.error(f"An unexpected error occurred: {str(e)}")

def run_mtr(target):
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


print(get_external_ip())