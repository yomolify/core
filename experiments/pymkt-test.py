from __future__ import absolute_import

import pymarketstore as pymkts

param = pymkts.Params('BTC', '1Min', 'OHLCV', limit=10)
cli = pymkts.Client()
reply = cli.query(param)
reply.first().df()