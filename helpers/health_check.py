import requests
import os
from telegram.ext import CallbackContext

APP_ENV_IS_DEV = True if os.environ.get("APP_ENV") == 'dev' else False
GROUP_IDS = [-630076873, -1001540246623]

def server_health_check(context: CallbackContext):
    r = requests.get("https://cityuge.com")
    print(r.status_code)
    if (not r.status_code == 200):
        for chat_id in GROUP_IDS:
            text = 'Server is down with status code: {}'.format(str(r.status_code))
            context.bot.sendMessage(chat_id=chat_id, text=text, parse_mode='HTML')