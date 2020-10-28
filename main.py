from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import time
import warnings
# import datetime
from datetime import datetime, timedelta
import os.path
import sys  # To find out the script name (in argv[0])
import json
import args
import logging
import fnmatch
import os
import pandas as pd
import glob
import importlib

from config import BINANCE, ENV, PRODUCTION, BASE, QUOTE, DEBUG, TRADING

if ENV == PRODUCTION:
    from ccxtbt import CCXTStore

import backtrader as bt
import backtrader_addons as bta
from analyzers import *
from btplotting import BacktraderPlotting, BacktraderPlottingLive
from btplotting.schemes import Blackly, Tradimo
from btplotting.analyzers import RecorderAnalyzer

from dicts import ExchangeCSVIndex, ExchangeDTFormat, Strategy, ExecType

from sizer.percent import FullMoney

args = args.parse()

_logger = logging.getLogger(__name__)


def format_dt_daily(dt):
    if len(dt) > 10:
        dt = dt[:-9]
    return datetime.strptime(dt, '%Y-%m-%d')


def format_dt_hourly(dt):
    if len(dt) > 19:
        dt = dt[:-4]
    dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    return dt


if ENV == PRODUCTION:  # Live trading with Binance
    with open('params.json', 'r') as f:
        params = json.load(f)
    cerebro = bt.Cerebro(quicknotify=True)

    config = {'apiKey': '',
              'secret': '',
              'enableRateLimit': True,
              'options': {
                  'defaultType': 'future',
              }
              }

    store = CCXTStore(exchange='binance', currency='USDT', config=config, retries=5, debug=False)

    broker_mapping = {
        'order_types': {
            bt.Order.Market: 'market',
            bt.Order.Limit: 'limit',
            bt.Order.Stop: 'STOP_MARKET',  # stop-loss for kraken, stop for bitmex
            bt.Order.StopLimit: 'stop limit'
        },
        'mappings': {
            'closed_order': {
                'key': 'status',
                'value': 'closed'
            },
            'canceled_order': {
                'key': 'result',
                'value': 1}
        }
    }


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

    # cerebro = bt.Cerebro()
    if TRADING == 'LIVE':
        broker = store.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)
    else:
        # cerebro.addstrategy(LiveDemoStrategy)
        cerebro.broker.setcash(10000.0)
    cerebro.addsizer(FullMoney)
    cerebro.addobserver(bta.observers.SLTPTracking)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addstrategy(Strategy[args.strategy], exectype=ExecType[args.exectype])

    cerebro.addanalyzer(RecorderAnalyzer)
    cerebro.addanalyzer(BacktraderPlottingLive, volume=True, scheme=Blackly(
        hovertool_timeformat='%F %R:%S'), lookback=12000)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')

    hist_start_date = datetime.utcnow() - timedelta(hours=1000)
    # hist_start_date = datetime.utcnow() - timedelta(minutes=1000)
    # hist_start_date = datetime.utcnow() - timedelta(minutes=1)
    dataname = "{}/{}".format(args.base, args.quote)
    data = store.getdata(dataname=dataname, name=dataname.replace('/', ''),
                         timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                         compression=60, ohlcv_limit=50, drop_newest=True, backfill_start=True)  # , historical=True)
    #  compression=1, ohlcv_limit=50, drop_newest=True, backfill_start=True) #, historical=True)

    cerebro.resampledata(data, timeframe=resample_timeframe, compression=resample_compression)

    # return the recorded bars attribute from the first strategy
    res = cerebro.run()
    return cerebro, res[0]


if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True)
    warnings.filterwarnings("ignore")
    print("Running in {} and {} trading".format(ENV, TRADING))

    if ENV == PRODUCTION:  # Live trading with Binance
        logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s', level=logging.INFO)
        cerebro, strat = _run_resampler(data_timeframe=bt.TimeFrame.Minutes,
                                        data_compression=60,
                                        # data_compression=1,
                                        resample_timeframe=bt.TimeFrame.Minutes,
                                        resample_compression=60,
                                        # resample_compression=1,
                                        runtime_seconds=60000,
                                        tick_interval=timedelta(seconds=60),
                                        start_delays=[None, None],
                                        num_gen_bars=[0, 10],
                                        num_data=2,
                                        )

    else:  # Backtesting with CSV file
        strategy_class = (args.strategy).split(".", 1)[1]
        strategy = getattr(importlib.import_module(f'strategies.{args.strategy}'), strategy_class)

        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        csvpath = '{}-{}-{}.csv'.format(args.exchange, args.ticker, args.data_timeframe)
        # datapath = os.path.join(modpath, 'data/{}'.format(csvpath))
        datapath = '../fetch-historical-data'

        # Single Coin
        if strategy_class == 'NLS1':
            data = bt.feeds.GenericCSVData(
                dataname=f"{datapath}/binance-{args.ticker}-1h.csv",
                dtformat=lambda x: format_dt_hourly(x),
                # dtformat=ExchangeDTFormat[args.exchange],
                open=ExchangeCSVIndex[args.exchange]['open'],
                high=ExchangeCSVIndex[args.exchange]['high'],
                low=ExchangeCSVIndex[args.exchange]['low'],
                close=ExchangeCSVIndex[args.exchange]['close'],
                volume=ExchangeCSVIndex[args.exchange]['volume'],
                fromdate=datetime(args.from_year, args.from_month, args.from_date),
                todate=datetime(args.to_year, args.to_month, args.to_date),
                timeframe=bt.TimeFrame.Minutes,
                compression=60,
                nullvalue=0.0,
                reverse=False)
            cerebro.adddata(data)

            resample_timeframes = dict(
                minutes=bt.TimeFrame.Minutes,
                daily=bt.TimeFrame.Days,
                weekly=bt.TimeFrame.Weeks,
                monthly=bt.TimeFrame.Months)

            # Use to backtest hourly timeframe on minute data
            # cerebro.resampledata(data,
            #                      timeframe=bt.TimeFrame.Minutes,
            #                      compression=60)
        # Altcoin Universe
        else:
            tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT',
                       'ETCUSDT', 'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT',
                       'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT',
                       'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT', 'ALGOUSDT', 'ZILUSDT']
            
            # All spot altcoins with one year historical data, stablecoins and badcoins removed
            # tickers = ['BTCUSDT', 'IOSTUSDT', 'XLMUSDT', 'BEAMUSDT', 'ZECUSDT', 'XMRUSDT', 'BANDUSDT', 'DUSKUSDT', 'CVCUSDT', 'BATUSDT',
            #          'TRXUSDT', 'TFUELUSDT', 'ONGUSDT', 'THETAUSDT', 'ADAUSDT', 'KEYUSDT', 'WAVESUSDT', 'MTLUSDT', 'IOTAUSDT',
            #          'TOMOUSDT', 'ICXUSDT', 'ONTUSDT', 'LTCUSDT', 'WINUSDT', 'ENJUSDT', 'HCUSDT', 'XRPUSDT',
            #          'OMGUSDT', 'FETUSDT', 'BNBUSDT', 'ONEUSDT', 'MFTUSDT', 'XTZUSDT', 'ZILUSDT', 'BTTUSDT', 'ATOMUSDT', 'ETHUSDT',
            #          'NANOUSDT', 'EOSUSDT', 'HOTUSDT', 'RENUSDT', 'NPXSUSDT', 'ALGOUSDT', 'FUNUSDT', 'ZRXUSDT',
            #          'MITHUSDT', 'PERLUSDT', 'GTOUSDT', 'LINKUSDT',
            # 'RVNUSDT', 'COSUSDT', 'ANKRUSDT', 'COCOSUSDT',
            #          'DASHUSDT', 'QTUMUSDT', 'DOCKUSDT', 'NULSUSDT',
            # 'NKNUSDT', 'PAXUSDT', 'ERDUSDT', 'FTMUSDT',
            #          'DOGEUSDT', 'MATICUSDT', 'CELRUSDT', 'VETUSDT',
            # 'HBARUSDT', 'CHZUSDT', 'WANUSDT', 'ETCUSDT',
            #          'DENTUSDT', 'NEOUSDT']

            # 'BCHABCUSDT', 'BCCUSDT','BUSDUSDT', 'USDCUSDT', 'USDSUSDT', 'TUSDUSDT',
            for ticker in tickers:
                data = bt.feeds.GenericCSVData(
                    open=ExchangeCSVIndex[args.exchange]['open'],
                    high=ExchangeCSVIndex[args.exchange]['high'],
                    low=ExchangeCSVIndex[args.exchange]['low'],
                    close=ExchangeCSVIndex[args.exchange]['close'],
                    volume=ExchangeCSVIndex[args.exchange]['volume'],
                    dataname=f"{datapath}/binance-{ticker}-1h.csv",
                    # dataname=f"{datapath}/binance-{ticker}-1d.csv",
                    dtformat=lambda x: format_dt_hourly(x),
                    # dtformat=lambda x: format_dt_daily(x),
                    fromdate=datetime(args.from_year, args.from_month, args.from_date),
                    todate=datetime(args.to_year, args.to_month, args.to_date),
                    timeframe=bt.TimeFrame.Minutes,
                    compression=60,
                    openinterest=-1,
                    nullvalue=0.0)
                cerebro.adddata(data, name=ticker)

        cerebro.broker.set_coc(True)
        cerebro.broker.setcash(10000.0)
        cerebro.addsizer(FullMoney)
        # cerebro.broker.setcommission(commission=0.0006)
        print('Starting {}'.format(args.strategy))
        cerebro.addobserver(bta.observers.SLTPTracking)
        cerebro.addobserver(bt.observers.DrawDown)
        cerebro.addstrategy(strategy, exectype=ExecType[args.exectype])
        # strats = cerebro.optstrategy(
        #     Strategy[args.strategy],
        #     period_sma_bitcoin=range(50, 52))

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    addAnalyzers(cerebro)

    stats = cerebro.run(maxcpus=16)
    stat = stats[0].analyzers

    print(args.strategy)
    print('======== PERFORMANCE ========\n')
    print('{}'.format(csvpath))
    print(
        '{}, {}, {} to {}, {}, {}'.format(args.from_year, args.from_month, args.from_date, args.to_year, args.to_month,
                                          args.to_date))
    getAnalysis(stat)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    if args.plot == True:
        p = BacktraderPlotting(style='candle', scheme=Blackly())
        cerebro.plot(p)
