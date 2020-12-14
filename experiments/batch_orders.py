import ccxt
from pprint import pprint


print('CCXT Version:', ccxt.__version__)

exchange = ccxt.binance({
    "apiKey": 'Gmaq6YHzd8APQkOjVo8uOrDuZZfBxDeBB3PTHWk2OMKlKy8AViwqEgbdypIYmexF',
    "secret": 'BlKuwz2uHkO9ZEPbGxt8Eomwdf0bEbOI41RHfMtmoYMesauyO3DRK4tYL1BIzh6G',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True,
    },
})

markets = exchange.load_markets()

# balance = exchange.fetch_balance()
# pprint(balance)
# TODO - hook in get_size_and_direction to batch order placement
symbol = 'BTC/USDT'
type = 'limit'
side = 'buy'  # or 'sell'
amount = 0.01
price = 5000

market = exchange.market(symbol)

orders = [
    {
        'symbol': market['id'],
        'side': side.upper(),
        'type': type.upper(),
        'quantity': exchange.amount_to_precision(symbol, amount),
        'price': exchange.price_to_precision(symbol, price),
        'timeInForce': 'GTC',
    }
]

orders = [exchange.encode_uri_component(exchange.json(order), safe=",") for order in orders]

exchange.verbose = True  # for debugging purposes

response = exchange.fapiPrivatePostBatchOrders({
    'batchOrders': '[' + ','.join(orders) + ']'
})

pprint(response)