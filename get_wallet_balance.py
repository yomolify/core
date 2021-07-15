import time
import ccxt
import json
import pprint
import asyncio
import aioredis
import msgpack
import datetime as dt
import sys


with open('params.json', 'r') as f:
    params = json.load(f)
exchange = ccxt.binance({
    'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
    'options': {
        'defaultType': 'future',
    },
    'apiKey': params["binance"]["apikey"],  # https://github.com/ccxt/ccxt/wiki/Manual#authentication
    'secret': params["binance"]["secret"],
})


async def cache_wallet(positions, assets):
    redis = await aioredis.create_redis_pool(
        'redis://localhost')
    await redis.set('positions', msgpack.packb(positions))
    await redis.set('assets', msgpack.packb(assets))

    positions = await redis.get('positions')
    assets = await redis.get('assets')

    positions = msgpack.unpackb(positions)
    assets = msgpack.unpackb(assets)
    positions_keys = list(positions[0].keys())
    positions_local = dict()
    for position in positions:
        for key in position:
            if float((position[b"positionAmt"]).decode()):
                positions_local[(position[b"symbol"]).decode()] = {
                    "size": float((position[b"positionAmt"]).decode()),
                    "entry_price": float((position[b"entryPrice"]).decode())
                }
    print(dt.datetime.now())
    for position in positions_local:
        print(f'{position}: {positions_local[position]}')

    redis.close()
    await redis.wait_closed()

while True:
    # if dt.datetime.now().second / 1 == 0:
    try:
        exchange_info = exchange.fetch_balance()["info"]
        positions = exchange_info["positions"]
        assets = exchange_info["assets"]
        # print(f'Margin Balance: {margin_balance}')
        # pprint.pprint(json.loads(json.dumps(margin_balance)))
        asyncio.run(cache_wallet(positions, assets))
    except Exception as e:
        print("ERROR: {}".format(sys.exc_info()[0]))
        print("{}".format(e))
    # time.sleep(1746)
    time.sleep(2)
