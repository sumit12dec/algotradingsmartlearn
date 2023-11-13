import json
import urllib
import pymongo
import requests
from kiteconnect import KiteConnect

host = "mongodb+srv://:@/?retryWrites=true&w=majority"
client = pymongo.MongoClient(host)
db = client['test']
my_token_collection = db["my_tokens"]

kite = KiteConnect(api_key="", debug=True)

# def send_message_bot(chat_id, text):
# 	url = 'https://api.telegram.org/<YOUR-BOT-TOKEN>/sendMessage'
# 	r = requests.post(url, {'chat_id': chat_id, 'text': text}).json()

def set_token(request_token):
    data = kite.generate_session(request_token, api_secret="")
    my_token_collection.update_one({"user_id":""}, { "$set": { "token": data["access_token"] } }, upsert=True)
    return data["access_token"]

def get_token():
    x = my_token_collection.find_one({"user_id": ""})
    return x["token"]

def place_order(received_data, txn_type="BUY"):
    stock_id = [urllib.parse.quote_plus(ts) for ts in received_data['stocks'].split(',')]
    place_at = [float(o) for o in received_data['trigger_prices'].split(',')]
    stop_at, book_at = zip(*[(round(_ - _*0.01, 1), round(_ + _*0.01, 1)) for _ in place_at])
    
    if txn_type == "SELL":
        stop_at, book_at = book_at, stop_at

    qty_to_buy = [int(500/abs(order_price - stop_loss)) for order_price, stop_loss in zip(place_at, stop_at)]
    kite.set_access_token(get_token())

    for tradingsymbol, quantity, execute_at, sl, tg in zip(stock_id, qty_to_buy, place_at, stop_at, book_at):
        order_id = kite.place_order(tradingsymbol=tradingsymbol, exchange="NSE", transaction_type=txn_type, quantity=quantity,
        order_type="LIMIT", price=execute_at, trigger_price=sl, product="MIS", validity="DAY", disclosed_quantity=0, 
        squareoff=0, stoploss=0, trailing_stoploss=0, variety='amo')
        # send_message_bot(<YOUR-CHAT-ID>, "{} Order placed for {} at {}, SL: {}, TG: {}".format(txn_type, tradingsymbol, execute_at, sl, tg))

def lambda_handler(event, context):
    query_dict = event.get('queryStringParameters', {})
    if event.get('rawPath') == '/set-token':
        return {'access_token': set_token(query_dict.get('request_token')), 'msg': 'Token was set successfully.'}
    if event.get('rawPath') == '/webhook':
        received_data = json.loads(event['body'])
        if received_data['scan_url'] == "near-day-high-108":
            place_order(received_data, txn_type="BUY")
