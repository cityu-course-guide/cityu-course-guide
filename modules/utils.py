import logging
import os
import certifi

from telegram.ext import ConversationHandler
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

APP_ENV_IS_DEV = True if os.environ.get("APP_ENV") == 'dev' else False
GROUP_IDS = [-630076873] if not APP_ENV_IS_DEV else [-1001540246623]
MONGODB_ATLAS_USERNAME = os.environ.get("MONGODB_ATLAS_USERNAME")
MONGODB_ATLAS_PASSWORD = os.environ.get("MONGODB_ATLAS_PASSWORD")
MONGODB_ATLAS_URL = os.environ.get("MONGODB_ATLAS_URL")
MONGODB_ATLAS_DATABASE = os.environ.get("MONGODB_ATLAS_DATABASE")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
ca = certifi.where()

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def end(update):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END

def get_mongo_atlas():
    mongo_path = 'mongodb+srv://{}:{}@{}/{}?retryWrites=true&w=majority'.format(MONGODB_ATLAS_USERNAME, MONGODB_ATLAS_PASSWORD, MONGODB_ATLAS_URL, MONGODB_ATLAS_DATABASE)
    client = MongoClient(mongo_path, tlsCAFile=ca)
    db = client['courseguide-dev']
    return db

def list_dicts_difference_by_key(list_1, list_2, key):
    result = []
    for l1 in list_1:
        found = False
        for l2 in list_2:
            if l1[key] == l2[key]:
                found = True
        if not found:
            result.append(l1)
    return result