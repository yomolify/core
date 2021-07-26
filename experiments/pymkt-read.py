from __future__ import absolute_import

import pymarketstore as pymkts
from datetime import datetime
import numpy as np
import pandas as pd
# client = Client("7leSzp8xkXUzLqJHiYpoz0aiY0iXsUWKp3mk4WWyA8gorADSuEKBeGXo2HQgVA2K", "neuxdUFrNaP6nE38ZSHHdpPtgvCldk3oeCGCfDzjVH0AJne6NKgukITUrLWCKBPD")

cli = pymkts.Client()


# TODO - Read data as 1Min OHCLV of one symbol
# while True:
# reply = cli.query(pymkts.Params('binancefutures_BTC-USDT', '1H', 'OHLCV')).first().df()
reply = cli.query(pymkts.Params('binancefutures_EOS-USDT', '1Min', 'OHLCV', start=datetime(2021, 2, 20), end=datetime(2021, 3, 5))).first().df()
# reply = cli.query(pymkts.Params('binancefutures_EOS-USDT', '1Min', 'OHLCV', start=datetime(2021, 4, 20), end=datetime(2021, 5, 5))).first().df()
print(reply)
#
#
# end = datetime.now()
# start = datetime(end.year - 1, end.month, end.day)
# reply = cli.query(pymkts.Params('binance_SUSHI-USDT', '1H', 'OHLCV', limit=99999, start=start, end=end)).first().df()
# print(reply)