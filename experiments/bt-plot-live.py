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
        # sma2 = bt.indicators.SMA(self.data1.close, subplot=True)
        rsi = bt.ind.RSI()
        # cross = bt.ind.CrossOver(sma1, sma2)

    def next(self):
        pos = len(self.data)
        if pos % self.p.modbuy == 0:
            if self.broker.getposition(self.datas[0]).size == 0:
                self.buy(self.datas[0], size=None)

        if pos % self.p.modsell == 0:
            if self.broker.getposition(self.datas[0]).size > 0:
                self.sell(self.datas[0], size=None)


def _get_trading_calendar(open_hour, close_hour, close_minute):
    cal = bt.TradingCalendar(open=datetime.time(hour=open_hour), close=datetime.time(hour=close_hour, minute=close_minute))
    return cal


with open('params.json', 'r') as f:
    params = json.load(f)

cerebro = bt.Cerebro(quicknotify=True)


# Add the strategy
# cerebro.addstrategy(TestStrategy)

# Create our store
config = {'apiKey': params["binance"]["apikey"],
          'secret': params["binance"]["secret"],
          'enableRateLimit': True,
          }


# IMPORTANT NOTE - Kraken (and some other exchanges) will not return any values
# for get cash or value if You have never held any BNB coins in your account.
# So switch BNB to a coin you have funded previously if you get errors
store = CCXTStore(exchange='binance', currency='BNB', config=config, retries=5, debug=False)


# Get the broker and pass any kwargs if needed.
# ----------------------------------------------
# Broker mappings have been added since some exchanges expect different values
# to the defaults. Case in point, Kraken vs Bitmex. NOTE: Broker mappings are not
# required if the broker uses the same values as the defaults in CCXTBroker.
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

# Get our data
# Drop newest will prevent us from loading partial data from incomplete candles
hist_start_date = datetime.utcnow() - timedelta(minutes=30)

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
    #  paper trading with bt.cerebro here, without it tries to place order on binance since it uses setbroker above
    # cerebro = bt.Cerebro()
    cerebro.addstrategy(LiveDemoStrategy)

    cerebro.addanalyzer(RecorderAnalyzer)

    cerebro.addanalyzer(BacktraderPlottingLive, volume=False, scheme=Blackly(
        hovertool_timeformat='%F %R:%S'), lookback=120)

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    data = store.getdata(dataname='BNB/USDT', name="BNBUSDT",
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                     compression=1, ohlcv_limit=50, drop_newest=True) #, historical=True)

    cerebro.resampledata(data, timeframe=resample_timeframe, compression=resample_compression)

    # return the recorded bars attribute from the first strategy
    res = cerebro.run()
    return cerebro, res[0]


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s', level=logging.INFO)
    print('gere')
    cerebro, strat = _run_resampler(data_timeframe=bt.TimeFrame.Minutes,
                                    data_compression=1,
                                    resample_timeframe=bt.TimeFrame.Minutes,
                                    resample_compression=1,
                                    runtime_seconds=60000,
                                    tick_interval=timedelta(seconds=60),
                                    start_delays=[None, None],
                                    num_gen_bars=[0, 10],
                                    num_data=2,
                                    )