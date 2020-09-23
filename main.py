from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings
import datetime
import os.path
import sys  # To find out the script name (in argv[0])
import json
import args

import backtrader as bt
import backtrader_addons as bta

from btplotting import BacktraderPlotting
from btplotting.schemes import Blackly, Tradimo

from dicts import ExchangeCSVIndex, ExchangeDTFormat, Strategy, ExecType 

from sizer.percent import FullMoney

args = args.parse()

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    cerebro = bt.Cerebro()
    # Get historical data
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    csvpath = '{}-{}-{}.csv'.format(args.exchange, args.ticker, args.data_timeframe)
    datapath = os.path.join(modpath, 'data/{}'.format(csvpath))

    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        dtformat=ExchangeDTFormat[args.exchange],
        open=ExchangeCSVIndex[args.exchange]['open'],
        high=ExchangeCSVIndex[args.exchange]['high'],
        low=ExchangeCSVIndex[args.exchange]['low'],
        close=ExchangeCSVIndex[args.exchange]['close'],
        volume=ExchangeCSVIndex[args.exchange]['volume'],
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
    # cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    cerebro.addobserver(bta.observers.SLTPTracking)

    cerebro.addstrategy(Strategy[args.strategy], exectype=ExecType[args.exectype])
    # cerebro.addstrategy(BollingerBands_template)

    stats = cerebro.run(**eval('dict(' + args.cerebro + ')'))
    stat = stats[0].analyzers
    
    print(args.strategy)
    print('======== PERFORMANCE ========\n')
    # print('{}'.format(csvpath))
    print('{}, {}, {} to {}, {}, {}'.format(args.from_year, args.from_month, args.from_date, args.to_year, args.to_month, args.to_date))
    print('Sharpe Ratio: ', json.dumps(stat.sharpe_ratio.get_analysis()["sharperatio"], indent=2))
    print('Max Drawdown: ', json.dumps(stat.drawdown.get_analysis().max.drawdown, indent=2))
    print('Number of Trades: ', json.dumps(stat.trade_analyzer.get_analysis().total.total, indent=2))
    # print('VWR: ', json.dumps(stat.vwr.get_analysis()["vwr"], indent=2))

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
    if args.plot:
        p = BacktraderPlotting(style='candle', scheme=Blackly())
        cerebro.plot(p)
