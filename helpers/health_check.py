import requests
import os

from telegram.ext import CallbackContext
from modules.utils import GROUP_IDS

APP_ENV_IS_DEV = True if os.environ.get("APP_ENV") == 'dev' else False

def server_health_check(context: CallbackContext):
    r = requests.get("https://cityuge.com")
    print('[Health Check]Server index status code: {}'.format(str(r.status_code)))
    ping = requests.get("https://cityuge.com/api/ping")
    print('[Health Check]Server ping status code: {}'.format(str(ping.status_code)))
    if (not r.status_code == 200 or not ping.status_code == 200):
        for chat_id in GROUP_IDS:
            text = '🚨🚨🚨 Server is down 🚨🚨🚨'
            text += '\nIndex page status code: {}'.format(str(r.status_code))
            text += '\nPing api status code: {}'.format(str(ping.status_code))
            context.bot.sendMessage(chat_id=chat_id, text=text, parse_mode='HTML')