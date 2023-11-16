import json
import pymongo
import urllib
from common import place_order, search_scrip

def inst_token(symbol, exchange='NSE'):
    # print("symbol::", symbol)
    status_code, res = search_scrip(symbol)
    if res["result"][0]:
        for most_close_match in res["result"]:
            if exchange == "NFO" and most_close_match["trading_symbol"] == symbol:
                instrument_token = int(most_close_match["token"])
                break
            elif exchange == "NSE" and most_close_match["trading_symbol"] == f"{symbol}-EQ":
                instrument_token = int(most_close_match["token"])
                product = "CNC"
                break
    return instrument_token
    

def get_payload(received_data, txn_type):
    stock_id = [urllib.parse.quote_plus(ts) for ts in received_data['stocks'].split(',')]
    place_at = [float(o) for o in received_data['trigger_prices'].split(',')]
    stop_at, book_at = zip(*[(round(_ - _*0.01, 1), round(_ + _*0.01, 1)) for _ in place_at])
    payloads = []
    if txn_type == "SELL":
        stop_at, book_at = book_at, stop_at

    qty_to_buy = [int(500/abs(order_price - stop_loss)) for order_price, stop_loss in zip(place_at, stop_at)]

    for tradingsymbol, quantity, execute_at, sl, tg in zip(stock_id, qty_to_buy, place_at, stop_at, book_at):
        instrument_token = inst_token(tradingsymbol)
        payloads.append({'price': execute_at, 'quantity': quantity, 'order_side': txn_type, 'instrument_token': instrument_token})
    return payloads
def lambda_handler(event, context):
    # print(client.positions())
    received_data = json.loads(event['body'])
    print(received_data)
    # token = get_user_token('DK2305664')
    if received_data['scan_url'] == "day-high":
        payloads = get_payload(received_data, txn_type="BUY")
        for payload in payloads:
            place_order(payload)

    if received_data['scan_url'] == "day-low":
        payloads = get_payload(received_data, txn_type="SELL")
        for payload in payloads:
            place_order(payload)
    return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
