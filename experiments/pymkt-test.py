from __future__ import absolute_import

import pymarketstore as pymkts
from datetime import datetime

end = datetime.now()
start = datetime(end.year - 1, end.month, end.day)

param = pymkts.Params('XBTUSD', '1H', 'OHLCV', limit=10, start=start, end=end)

cli = pymkts.Client()
reply = cli.query(param)
reply.first().df()