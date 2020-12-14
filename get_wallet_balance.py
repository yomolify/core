import time
import ccxt
import json
import pprint
from pymemcache.client import base
client = base.Client(('localhost', 11211))
with open('params.json', 'r') as f:
    params = json.load(f)
exchange = ccxt.binance({
    'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
    'options': {
        'defaultType': 'future',
    },
    'apiKey': params["binance-lh"]["apikey"],  # https://github.com/ccxt/ccxt/wiki/Manual#authentication
    'secret': params["binance-lh"]["secret"],
})

while True:
    margin_balance = exchange.fetch_balance()["info"]["totalMarginBalance"]
    # margin_balance = exchange.fetch_balance()
    client.set('margin_balance', margin_balance)
    # print(f'Margin Balance: {margin_balance}')
    # pprint.pprint(json.loads(json.dumps(margin_balance)))
    time.sleep(2)
    print(float(client.get('margin_balance').decode()))
