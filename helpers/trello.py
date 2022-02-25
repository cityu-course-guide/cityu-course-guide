import os
import requests
import json

from dotenv import load_dotenv
from telegram.ext import CallbackContext

from modules.utils import get_mongo_atlas
from modules.utils import list_dicts_difference_by_key
from modules.utils import GROUP_IDS
load_dotenv()

TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY")
TRELLO_API_TOKEN = os.environ.get("TRELLO_API_TOKEN")
MONGODB_ATLAS_USERNAME = os.environ.get("MONGODB_ATLAS_USERNAME")
MONGODB_ATLAS_PASSWORD = os.environ.get("MONGODB_ATLAS_PASSWORD")
MONGODB_ATLAS_URL = os.environ.get("MONGODB_ATLAS_URL")
MONGODB_ATLAS_DATABASE = os.environ.get("MONGODB_ATLAS_DATABASE")

board_id = '5f5dd769d2587924d54ae999'
trello_card_collection_name = 'trellocards'

def get_trello_lists():
    r = requests.get('https://api.trello.com/1/boards/{}/lists?key={}&token={}'.format(board_id, TRELLO_API_KEY, TRELLO_API_TOKEN)).text
    lists = json.loads(r)
    return lists

def get_trello_cards(lists):
    all_cards = []
    for list in lists:
        r = requests.get('https://api.trello.com/1/lists/{}/cards?key={}&token={}'.format(list['id'], TRELLO_API_KEY, TRELLO_API_TOKEN)).text
        cards = json.loads(r)
        for card in cards:
            all_cards.append({
                'name': card['name'],
                'id': card['id'],
                'url': card['shortUrl'],
                'list': list['name'],
                'listId': list['id'],
            })
    return all_cards

def get_db_cards():
    db = get_mongo_atlas()
    collection = db[trello_card_collection_name]
    items = collection.find()
    result = []
    for item in items:
        result.append(item)
    return result

def insert_db_cards(cards):
    db = get_mongo_atlas()
    collection = db[trello_card_collection_name]
    collection.insert_many(cards)

def update_db_cards(cards):
    db = get_mongo_atlas()
    collection = db[trello_card_collection_name]
    for card in cards:
        collection.update_one({'id': card['id']}, {'$set': {'name': card['name'], 'list': card['list'], 'listId': card['listId'], 'url': card['url']}})

def remove_db_cards(cards):
    db = get_mongo_atlas()
    collection = db[trello_card_collection_name]
    for card in cards:
        collection.delete_one({'_id': card['_id']})

def get_updated_cards(list_1, list_2, key):
    result = []
    for c1 in list_1:
        for c2 in list_2:
            if c1['id'] == c2['id'] and not c1[key] == c2[key]:
                result.append(c1)
    return result

def check_cards_update(context: CallbackContext):
    print('[Trello]Started DB crawling...')
    db_cards = get_db_cards()

    print('[Trello]Started Trello crawling...')
    trello_lists = get_trello_lists()
    trello_cards = get_trello_cards(trello_lists)

    print('[Trello]DB Card: {} | Trello Card: {}'.format(str(len(db_cards)), str(len(trello_cards))))

    new_cards = list_dicts_difference_by_key(trello_cards, db_cards, 'id')
    removed_cards = list_dicts_difference_by_key(db_cards, trello_cards, 'id')
    renamed_cards = get_updated_cards(trello_cards, db_cards, 'name')
    moved_cards = get_updated_cards(trello_cards, db_cards, 'listId')

    print('[Trello]New Card: {} | Removed Card: {} | Renamed Card: {} | Moved Card: {}'.format(str(len(new_cards)), str(len(removed_cards)), str(len(renamed_cards)), str(len(moved_cards))))

    has_update = False
    if len(new_cards) > 0:
        has_update = True
        insert_db_cards(new_cards)
    if len(removed_cards) > 0:
        has_update = True
        remove_db_cards(removed_cards)
    if len(renamed_cards) > 0:
        has_update = True
        update_db_cards(renamed_cards)
    if len(moved_cards) > 0:
        has_update = True
        update_db_cards(moved_cards)

    print('[Trello]DB Updated')

    text = 'Trello Updates:'
    print('[Trello]Updating Message')
    for card in new_cards:
        text += '\nCard "<a href="{}">{}</a>" has been added to "{}"'.format(card['url'], card['name'], card['list'])

    for card in removed_cards:
        text += '\nCard "<a href="{}">{}</a>" has been removed'.format(card['url'], card['name'], card['list'])

    for card in renamed_cards:
        old_card = next(item for item in db_cards if item['id'] == card['id'])
        text += '\nCard "{}" has been renamed to "<a href="{}">{}</a>"'.format(old_card['name'], card['url'], card['name'])

    for card in moved_cards:
        text += '\nCard "<a href="{}">{}</a>" has been moved to "{}"'.format(card['url'], card['name'], card['list'])

    for chat_id in GROUP_IDS:
        if has_update:
            context.bot.sendMessage(chat_id=chat_id, text=text, parse_mode='HTML')
