#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ccxtbt import CCXTStore
import backtrader as bt
from datetime import datetime, timedelta
import json
import logging

import backtrader as bt

from btplotting import BacktraderPlottingLive
from btplotting.schemes import Blackly
from btplotting.analyzers import RecorderAnalyzer
from btplotting.feeds import FakeFeed

_logger = logging.getLogger(__name__)

class LiveDemoStrategy(bt.Strategy):
    params = (
        ('modbuy', 2),
        ('modsell', 3),
    )

    def __init__(self):
        pass
        sma1 = bt.indicators.SMA(self.data0.close, subplot=True)
        rsi = bt.ind.RSI()

with open('params.json', 'r') as f:
    params = json.load(f)

cerebro = bt.Cerebro(quicknotify=True)

config = {'apiKey': params["binance"]["apikey"],
          'secret': params["binance"]["secret"],
          'enableRateLimit': True,
          }

store = CCXTStore(exchange='binance', currency='BNB', config=config, retries=5, debug=False)

broker_mapping = {
    'order_types': {
        bt.Order.Market: 'market',
        bt.Order.Limit: 'limit',
        bt.Order.Stop: 'stop-loss', #stop-loss for kraken, stop for bitmex
        bt.Order.StopLimit: 'stop limit'
    },
    'mappings':{
        'closed_order':{
            'key': 'status',
            'value':'closed'
        },
        'canceled_order':{
            'key': 'result',
            'value':1}
    }
}

broker = store.getbroker(broker_mapping=broker_mapping)
cerebro.setbroker(broker)

def _run_resampler(data_timeframe,
                   data_compression,
                   resample_timeframe,
                   resample_compression,
                   runtime_seconds=27,
                   starting_value=200,
                   tick_interval=timedelta(seconds=1),
                   num_gen_bars=None,
                   start_delays=None,
                   num_data=1,
                   ) -> bt.Strategy:
    _logger.info("Constructing Cerebro")
    cerebro = bt.Cerebro()
    cerebro.addstrategy(LiveDemoStrategy)

    cerebro.addanalyzer(RecorderAnalyzer)

    cerebro.addanalyzer(BacktraderPlottingLive, volume=True, scheme=Blackly(
        hovertool_timeformat='%F %R:%S'), lookback=12000)

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)

    hist_start_date = datetime.utcnow() - timedelta(hours=1000)
    data = store.getdata(dataname='BNB/USDT', name="BNBUSDT",
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                     compression=60, ohlcv_limit=50, drop_newest=True, backfill_start=True) #, historical=True)

    cerebro.resampledata(data, timeframe=resample_timeframe, compression=resample_compression)

    # return the recorded bars attribute from the first strategy
    res = cerebro.run()
    return cerebro, res[0]

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s', level=logging.INFO)
    cerebro, strat = _run_resampler(data_timeframe=bt.TimeFrame.Minutes,
                                    data_compression=60,
                                    resample_timeframe=bt.TimeFrame.Minutes,
                                    resample_compression=60,
                                    runtime_seconds=60000,
                                    tick_interval=timedelta(seconds=60),
                                    start_delays=[None, None],
                                    num_gen_bars=[0, 10],
                                    num_data=2,
                                    )