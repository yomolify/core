import time
import ccxt
import json
import pprint
# import redis
import asyncio
import aioredis
import msgpack
import datetime as dt


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


async def cache_wallet(positions, assets):
    redis = await aioredis.create_redis_pool(
        'redis://localhost')
    await redis.set('positions', msgpack.packb(positions))
    await redis.set('assets', msgpack.packb(assets))
    positions = await redis.get('positions')
    assets = await redis.get('assets')
    print(msgpack.unpackb(positions))
    print(msgpack.unpackb(assets))
    redis.close()
    await redis.wait_closed()

while True:
    # if dt.datetime.now().second / 1 == 0:
    exchange_info = exchange.fetch_balance()["info"]
    positions = exchange_info["positions"]
    assets = exchange_info["assets"]
    # print(f'Margin Balance: {margin_balance}')
    # pprint.pprint(json.loads(json.dumps(margin_balance)))
    asyncio.run(cache_wallet(positions, assets))
    time.sleep(20)
        # print(float(client.get('margin_balance').decode()))




# positions: {
#     "ALPHAUSDT": {
#         "unrealizedProfit":
#
#     }
#
# }