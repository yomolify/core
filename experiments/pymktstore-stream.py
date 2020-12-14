import pymarketstore as pymkts

conn = pymkts.StreamConn('ws://localhost:5993/ws')


@conn.on(r'^binancefutures_BTC-USDT/')
def on_btc(conn, msg):
    print(msg['data'])
    # print(msg['data']['Epoch'])


conn.run(['binancefutures_BTC-USDT/1Min/OHLCV'])  # runs until exception

# on_btc()