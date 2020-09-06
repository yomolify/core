from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import os.path
import sys  # To find out the script name (in argv[0])

import backtrader as bt

from btplotting import BacktraderPlotting
from btplotting.schemes import Blackly, Tradimo

from strategies.L7 import L7
from sizer.percent import FullMoney

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Core'
        )
    )

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

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--strat', '--strategy', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')


    return parser.parse_args()

args = parse_args()

ExchangeCSVIndices = {
    'bitmex': {'open': 2, 'high': 3, 'low': 4, 'close': 5, 'volume': 7},
    'binance': {'open': 2, 'high': 3, 'low': 4, 'close': 5, 'volume': 7},
    'bitfinex': {'open': 1, 'high': 3, 'low': 4, 'close': 2, 'volume': 5}
    # 'bitfinex': {'open': 0, 'high': 2, 'low': 3, 'close': 1, 'volume': 4}
}

ExchangeDTFormat = {
    'bitmex': "%Y-%m-%d %H:%M:%S+00:00",
    'binance': '%Y-%m-%d %H:%M:%S',
    'bitfinex': lambda x: datetime.datetime.utcfromtimestamp(int(x[:-3]))
    # dtformat=('%b %d, %Y'),
}

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # cerebro.addstrategy(L7)
    cerebro.addstrategy(L7, **eval('dict(' + args.strat + ')'))

    # Get historical data
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    csvpath = '{}-{}-{}.csv'.format(args.exchange, args.ticker, args.data_timeframe)
    datapath = os.path.join(modpath, 'data/{}'.format(csvpath))
    # datapath = os.path.join(modpath, '../Bitfinex-historical-data/BTCUSD/Candles_1m/2019/merged.csv')

    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        dtformat=ExchangeDTFormat[args.exchange],
        open=ExchangeCSVIndices[args.exchange]['open'],
        high=ExchangeCSVIndices[args.exchange]['high'],
        low=ExchangeCSVIndices[args.exchange]['low'],
        close=ExchangeCSVIndices[args.exchange]['close'],
        volume=ExchangeCSVIndices[args.exchange]['volume'],
        fromdate=datetime.datetime(args.from_year, args.from_month, args.from_date),
        todate=datetime.datetime(args.to_year, args.to_month, args.to_date),
        timeframe=bt.TimeFrame.Minutes, 
        compression=1,
        nullvalue=0.0,
        reverse=False)

    resample_timeframes = dict(
        minutes=bt.TimeFrame.Minutes,
        daily=bt.TimeFrame.Days,
        weekly=bt.TimeFrame.Weeks,
        monthly=bt.TimeFrame.Months)

    # Bitfinex
    cerebro.resampledata(data,
                         timeframe=bt.TimeFrame.Minutes,
                         compression=60)
    # cerebro.adddata(data)

    cerebro.broker.setcash(10000.0)
    cerebro.addsizer(FullMoney)
    # cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name='transactions')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')

    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    thestrats = cerebro.run(**eval('dict(' + args.cerebro + ')'))
    thestrat = thestrats[0]

    print('\nSharpe Ratio:', thestrat.analyzers.sharpe_ratio.get_analysis())
    print('\nReturns:', thestrat.analyzers.returns.get_analysis())
    print('\nAnnual Return:', thestrat.analyzers.annual_return.get_analysis())
    print('\nMaximum Drawdown:', thestrat.analyzers.drawdown.get_analysis())
    print('\nTrade Analyzer:', thestrat.analyzers.trade_analyzer.get_analysis())
    # print('\nTransactions:', thestrat.analyzers.transactions.get_analysis())
    print('\nVariability-Weighted Return:', thestrat.analyzers.vwr.get_analysis())
    print('\nSQN:', thestrat.analyzers.sqn.get_analysis())

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    p = BacktraderPlotting(style='candle', scheme=Tradimo())
    cerebro.plot(p)

# self.log('Low => {}'.format(self.low))

