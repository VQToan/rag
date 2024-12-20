import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_message(msg):
    url = os.getenv('NOTI_SERVICE_URL') + '/notifications/spaces/ai-hub/messages'
    response = requests.get(
        url,
        params={
            'content': f'[TRIPGO-HOTEL][ERROR]: {msg}',
        }
    )
    return response.text


class NotiErrorHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        send_message(log_entry)
