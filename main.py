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

def parse_args():
    parser = argparse.ArgumentParser(description='Core')

    # parser.add_argument('--dataname', default='', required=False,
    #                     help='File Data to Load')

    parser.add_argument('--exchange', default='', required=False,
                        help='Exchange')

    parser.add_argument('--ticker', default='', required=False,
                        help='Ticker')
    
    parser.add_argument('--data_timeframe', default='', required=False,
                        help='Timeframe of provided data')

    parser.add_argument('--resample_timeframe', default='weekly', required=False,
                        choices=['daily', 'weekly', 'monhtly'],
                        help='Timeframe to resample to')
    
    parser.add_argument('--compression', default=1, required=False, type=int,
                        help='Compress n bars into 1')

    # Backtest from & to datetime
    parser.add_argument('--from_date', default='', required=False,
                        type=int, help='From date')
    parser.add_argument('--from_month', default='', required=False,
                        type=int, help='From month')
    parser.add_argument('--from_year', default='', required=False,
                        type=int, help='From year')
    parser.add_argument('--to_date', default='', required=False,
                        type=int, help='To Date')
    parser.add_argument('--to_month', default='', required=False,
                        type=int, help='To month')
    parser.add_argument('--to_year', default='', required=False,
                        type=int, help='To year')

    return parser.parse_args()

args = parse_args()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(L7)

    # Get historical data
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    csvpath = '{}-{}-{}.csv'.format(args.exchange, args.ticker, args.data_timeframe)
    datapath = os.path.join(modpath, 'data/{}'.format(csvpath))

    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        # Bitmex
        dtformat=("%Y-%m-%d %H:%M:%S+00:00"), 
        # Bitfinex
        # dtformat=(1), 
        # dtformat=('%b %d, %Y'),
        # dtformat=lambda x: datetime.datetime.utcfromtimestamp(int(x[:-3])),
        # tmformat=None,

        # Bitfinex
        # open=2,
        # high=3,
        # low=4,
        # close=1,
        # volume=5,

        # Bitmex
        open=2,
        high=3,
        low=4,
        close=5,
        volume=7,

        # BITSTAMP
        # fromdate=datetime.datetime(2016, 4, 1),
        # todate=datetime.datetime(2018, 4, 1),

        # BITFINEX
        fromdate=datetime.datetime(args.from_year, args.from_month, args.from_date),
        todate=datetime.datetime(args.to_year, args.to_month, args.to_date),

        # BITMEX
        # fromdate=datetime.datetime(2013, 4, 25),
        # todate=datetime.datetime(2020, 8, 26),

        # BINANCE
        # fromdate=datetime.datetime(2017, 8, 17),
        # todate=datetime.datetime(2020, 8, 1),

        nullvalue=0.0,
        # Do not pass values after this date
        reverse=False)

    resample_timeframes = dict(
        minutes=bt.TimeFrame.Minutes,
        daily=bt.TimeFrame.Days,
        weekly=bt.TimeFrame.Weeks,
        monthly=bt.TimeFrame.Months)

    # Bitmex
    # cerebro.resampledata(data,
    #                      timeframe=tframes["minutes"],
    #                      compression=60)

    # Bitfinex
    cerebro.resampledata(data,
                         timeframe=resample_timeframes["daily"],
                         compression=1)
    # cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    p = BacktraderPlotting(style='candle', scheme=Blackly())
    # cerebro.plot(p)



# self.log('Low => {}'.format(self.low))

