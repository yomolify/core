from __future__ import absolute_import

import pymarketstore as pymkts
from datetime import datetime

end = datetime.now()
start = datetime(end.year - 1, end.month, end.day)

param = pymkts.Params('binance_SUSHI-USDT', '1H', 'OHLCV', limit=99999, start=start, end=end)

cli = pymkts.Client()
reply = cli.query(param)
print(reply.first().df())
