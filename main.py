from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import os.path
import sys  # To find out the script name (in argv[0])

import backtrader as bt

from btplotting import BacktraderPlotting
from btplotting.schemes import Blackly

from strategies.L7 import L7

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(L7)
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'data/bitstampUSD_1-min_data_2015-04-01_to_2018-04-01.csv')
    datapath = os.path.join(modpath, 'data/bitmex-XBTUSD-1h.csv')
    # datapath = os.path.join(modpath, 'data/BTCUSDT-1h.csv')

    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        dtformat=("%Y-%m-%d %H:%M:%S+00:00"),
        open=2,
        high=3,
        low=4,
        close=5,
        volume=7,

        # BITSTAMP
        # fromdate=datetime.datetime(2016, 4, 1),
        # todate=datetime.datetime(2018, 4, 1),

        # BITMEX
        fromdate=datetime.datetime(2015, 9, 25),
        todate=datetime.datetime(2020, 8, 26),

        # BINANCE
        # fromdate=datetime.datetime(2017, 8, 17),
        # todate=datetime.datetime(2020, 8, 1),

        nullvalue=0.0,
        # Do not pass values after this date
        reverse=False)

    tframes = dict(
        minutes=bt.TimeFrame.Minutes,
        daily=bt.TimeFrame.Days,
        weekly=bt.TimeFrame.Weeks,
        monthly=bt.TimeFrame.Months)

    cerebro.resampledata(data,
                         timeframe=tframes["minutes"],
                         compression=60)
    # cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    p = BacktraderPlotting(style='candle', scheme=Blackly())
    cerebro.plot(p)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--dataname', default='', required=False,
                        help='File Data to Load')

    parser.add_argument('--timeframe', default='weekly', required=False,
                        choices=['daily', 'weekly', 'monhtly'],
                        help='Timeframe to resample to')

    parser.add_argument('--compression', default=1, required=False, type=int,
                        help='Compress n bars into 1')

    return parser.parse_args()

args = parse_args()

# self.log('Low => {}'.format(self.low))

