from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import warnings
import datetime
import os.path
import sys  # To find out the script name (in argv[0])
import json

import backtrader as bt
import backtrader_addons as bta

from btplotting import BacktraderPlotting
from btplotting.schemes import Blackly, Tradimo

from strategies import BuyHold, BollingerBands_template
from strategies.BollingerBands import L1, L2, L3, L4, L5, L6, L7, LS1

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

    parser.add_argument('--strategy', required=True, default='',
                        metavar='kwargs')
    parser.add_argument('--exectype', required=True, default='',
                        metavar='kwargs')

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

Strategy = {
    'BollingerBands.L1': L1.L1,
    'BollingerBands.L2': L2.L2,
    'BollingerBands.L3': L3.L3,
    'BollingerBands.L4': L4.L4,
    'BollingerBands.L5': L5.L5,
    'BollingerBands.L6': L6.L6,
    'BollingerBands.L7': L7.L7,
    'BollingerBands.LS1': LS1.LS1,
    'BuyHold.BuyAndHold_Buy': BuyHold.BuyAndHold_Buy,
    'BuyHold.BuyAndHold_Target': BuyHold.BuyAndHold_Target,
    'BuyHold.BuyAndHold_Target': BuyHold.BuyAndHold_Target,
    'BuyHold.BuyAndHold_More': BuyHold.BuyAndHold_More,
    'BuyHold.BuyAndHold_More_Fund': BuyHold.BuyAndHold_More_Fund,
}

ExecType = {
    'Limit': bt.Order.Limit,
    'Market': bt.Order.Market,
}

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    cerebro = bt.Cerebro()
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
                        #  compression=720)
    # cerebro.adddata(data)

    cerebro.broker.setcash(10000.0)
    cerebro.addsizer(FullMoney)
    # cerebro.broker.setcommission(commission=0.001)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Years, factor=365)
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', factor=365)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name='transactions')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    cerebro.addobserver(bta.observers.SLTPTracking)

    cerebro.addstrategy(Strategy[args.strategy], exectype=ExecType[args.exectype])
    # cerebro.addstrategy(BollingerBands_template)

    stats = cerebro.run(**eval('dict(' + args.cerebro + ')'))
    stat = stats[0].analyzers
    
    print(args.strategy)
    print('======== PERFORMANCE ========\n')
    print('Sharpe Ratio: ', json.dumps(stat.sharpe_ratio.get_analysis()["sharperatio"], indent=2))
    print('Max Drawdown: ', json.dumps(stat.drawdown.get_analysis().max.drawdown, indent=2))
    print('Number of Trades: ', json.dumps(stat.trade_analyzer.get_analysis().total.total, indent=2))
    print('VWR: ', json.dumps(stat.vwr.get_analysis()["vwr"], indent=2))

    # print(json.dumps(stat.analyzers.returns.get_analysis(), indent=2))
    # print(json.dumps(stat.analyzers.annual_return.get_analysis(), indent=2))

    # print('\nSharpe Ratio:', stat.analyzers.sharpe_ratio.get_analysis())
    # print('\nReturns:', stat.analyzers.returns.get_analysis())
    # print('\nAnnual Return:', stat.analyzers.annual_return.get_analysis())
    # print('\nMaximum Drawdown:', stat.analyzers.drawdown.get_analysis())
    # print('\nTrade Analyzer:', stat.analyzers.trade_analyzer.get_analysis())
    # print('\nTransactions:', stat.analyzers.transactions.get_analysis())
    # print('\nVariability-Weighted Return:', stat.analyzers.vwr.get_analysis())
    # print('\nSQN:', stat.analyzers.sqn.get_analysis())

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    p = BacktraderPlotting(style='candle', scheme=Blackly())
    # cerebro.plot(p)
