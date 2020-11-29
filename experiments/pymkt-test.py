from __future__ import absolute_import

import pymarketstore as pymkts
from datetime import datetime
import numpy as np
import pandas as pd
from binance.websockets import BinanceSocketManager
from binance.client import Client
client = Client("7leSzp8xkXUzLqJHiYpoz0aiY0iXsUWKp3mk4WWyA8gorADSuEKBeGXo2HQgVA2K", "neuxdUFrNaP6nE38ZSHHdpPtgvCldk3oeCGCfDzjVH0AJne6NKgukITUrLWCKBPD")

cli = pymkts.Client()

# TODO - Write tick data of all symbols to Marketstore using websockets


def process_message(msg):
    # print("Price: {}".format(msg['p']))
    # print("Trade Time: {}".format(msg['T']))
    price = msg['p']
    timestamp = msg['T']
    # print(pd.Timestamp('2017-01-01 00:00').value / 10 ** 9)
    # print(timestamp)
    # print(pd.Timestamp(f'{timestamp}'))
    data1 = np.array([(pd.Timestamp('2017-01-01 00:00').value / 10 ** 9, 10.0)], dtype=[('Epoch', 'i8'), ('Ask', 'f4')])
    data2 = np.array([(timestamp / 1000, price)], dtype=[('Epoch', 'i8'), ('Price', 'f4')])

    # print(data1)
    # print(data2)
    # data = np.array([(timestamp, 10.0)], dtype=[('Epoch', 'i8'), ('Price', 'f4')])
    cli.write(data2, 'TEST_BTCUSDA/1Min/Tick')
    print(f"writing {data2}")


bm = BinanceSocketManager(client)
# start any sockets here, i.e a trade socket
conn_key = bm.start_trade_socket('BTCUSDT', process_message)
# then start the socket manager
bm.start()

# TODO - Read data as 1Min OHCLV of one symbol
# reply = cli.query(pymkts.Params('TEST_BTCUSDT', '1Min', 'Tick')).first().df()
# print(reply)
#
#
# end = datetime.now()
# start = datetime(end.year - 1, end.month, end.day)
# reply = cli.query(pymkts.Params('binance_SUSHI-USDT', '1H', 'OHLCV', limit=99999, start=start, end=end)).first().df()
# print(reply)