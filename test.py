import os
import requests
import json

from dotenv import load_dotenv
from telegram.ext import CallbackContext

from modules.utils import get_mongo_atlas
from modules.utils import list_dicts_difference_by_key

load_dotenv()

TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY")
TRELLO_API_TOKEN = os.environ.get("TRELLO_API_TOKEN")
MONGODB_ATLAS_USERNAME = os.environ.get("MONGODB_ATLAS_USERNAME")
MONGODB_ATLAS_PASSWORD = os.environ.get("MONGODB_ATLAS_PASSWORD")
MONGODB_ATLAS_URL = os.environ.get("MONGODB_ATLAS_URL")
MONGODB_ATLAS_DATABASE = os.environ.get("MONGODB_ATLAS_DATABASE")

board_id = '5f5dd769d2587924d54ae999'

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
    collection = db['trellocard']
    items = collection.find()
    return items

def insert_db_cards(cards):
    db = get_mongo_atlas()
    collection = db['trellocard']
    collection.insert_many(cards)

def update_db_cards(cards):
    db = get_mongo_atlas()
    collection = db['trellocard']
    for card in cards:
        collection.update_one({'_id': card['_id']}, {'$set': {'name': card['name'], 'list': card['list'], 'listId': card['listId'], 'url': card['url']}})

def remove_db_cards(cards):
    db = get_mongo_atlas()
    collection = db['trellocard']
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
    db_cards = get_db_cards()

    trello_lists = get_trello_lists()
    trello_cards = get_trello_cards(trello_lists)
    new_cards = list_dicts_difference_by_key(trello_cards, db_cards, 'id')
    removed_cards = list_dicts_difference_by_key(db_cards, trello_cards, 'id')
    renamed_cards = get_updated_cards(trello_cards, db_cards, 'list')
    moved_cards = get_updated_cards(trello_cards, db_cards, 'listId')

    insert_db_cards(new_cards)
    remove_db_cards(removed_cards)
    update_db_cards(renamed_cards)
    update_db_cards(moved_cards)


    text = ''
    for card in new_cards:
        text += 'Card "{}" has been added to "{}"\n'.format(card['name'], card['list'])

    for card in removed_cards:
        text += 'Card "{}" has been removed\n'.format(card['name'], card['list'])

    for card in renamed_cards:
        old_card = next(item for item in db_cards if item['id'] == card['id'])
        text += 'Card "{}" has been renamed to "{}"\n'.format(old_card['name'], card['name'])

    for card in moved_cards:
        text += 'Card "{}" has been moved to "{}"\n'.format(card['name'], card['list'])

db = get_mongo_atlas()
db['trellocard'].drop()