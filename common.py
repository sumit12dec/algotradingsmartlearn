import pymongo
import requests
import json
host = ""

client = pymongo.MongoClient(host)
db = client['test']
my_token_collection = db["my_tokens"]

def get_user_token(user_id):
    token = my_token_collection.find_one({"user_id": user_id})
    return token['token']

headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {get_user_token("DK2305664")}'}

def place_order(payload):
    data = {
        "exchange": 'NSE',
        "instrument_token": payload['instrument_token'],
        "client_id": 'DK2305664',
        "order_type": 'LIMIT',
        "amo": 'false',
        "price": payload['price'],
        "quantity": payload['quantity'],
        "disclosed_quantity": 0,
        "validity": 'DAY',
        "product": 'CNC',
        "order_side": payload['order_side'],
        "device": "api",
        "user_order_id": 10002,
        "trigger_price": 0,
        "execution_type": 'REGULAR'
    }
    print(headers, "============")
    res = requests.post('https://spark.jainam.in/api/v1/orders', json=data, headers=headers)
    print(res.json(), "res from jainam")


def search_scrip(key):
    res = requests.get(f'https://spark.jainam.in/api/v1/search?key={key}', headers=headers)
    return res.status_code, res.json()
