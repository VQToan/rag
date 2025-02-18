import os

import requests

from src.config import logger


def get_news(id):
    try:
        url = f'{os.getenv("NEWS_API_URL")}/news/{id}'
        headers = {
            'siteKey': os.getenv('SITE_KEY'),
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json().get('isOK', False):
            return response.json().get('result')
        return None
    except Exception as e:
        logger.error(f'Error: {e}')
        return None
