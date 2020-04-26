import os
import logging
from bot import env

BOT_API_KEY = os.environ.get('BOT_API_KEY')

PROXY_URL = os.environ.get('PROXY_URL')
PROXY_USERNAME = os.environ.get('PROXY_USERNAME')
PROXY_PASSWORD = os.environ.get('PROXY_PASSWORD')

PROXY = {
    'proxy_url': PROXY_URL,
    'urllib3_proxy_kwargs':
        {
            'username': PROXY_USERNAME,
            'password': PROXY_PASSWORD
        }
}

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )