from telegram.ext import Updater, CommandHandler, Filters, MessageHandler

import os
import time
from dotenv import load_dotenv

from modules.utils import *
from helpers.health_check import *

load_dotenv()

APP_ENV_IS_DEV = True if os.environ.get("APP_ENV") == 'dev' else False
TOKEN = os.environ.get("TOKEN")
PORT = int(os.environ.get("PORT", "8443"))

def main():
    print('=======================================================')
    if APP_ENV_IS_DEV:
        print('Development Environment...')
    else:
        print('Production Environment...')
    print('=======================================================')
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True, workers=6)

    dp = updater.dispatcher

    # Command handler
    dp.add_handler(CommandHandler("help", help))

    # Message handler

    # Conversation handler

    # Error handler
    dp.add_error_handler(error)

    # Scheduled tasks

    j = updater.job_queue
    j.run_once(server_health_check, 1)

    # Start the Bot
    if APP_ENV_IS_DEV:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0",
                              port=int(PORT),
                              url_path=TOKEN)
        updater.bot.setWebhook('https://cityuge-tg-bot.herokuapp.com/' + TOKEN)

    time.sleep(5)
    updater.stop()


if __name__ == '__main__':
    main()

'''
'''
