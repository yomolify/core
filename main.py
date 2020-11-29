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

strategy_class = args.strategy.split(".", 1)[1]
strategy = getattr(importlib.import_module(f'strategies.{args.strategy}'), strategy_class)

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
    cerebro = bt.Cerebro(quicknotify=True, exactbars=True)

    config = {'apiKey': params["binance-akanksha"]["apikey"],
              'secret': params["binance-akanksha"]["secret"],
              'enableRateLimit': True,
              'options': {
                  'defaultType': 'future',
              }
              }

    store = CCXTStore(exchange='binance', currency='USDT', config=config, retries=5, debug=False)

    broker_mapping = {
        'order_types': {
            bt.Order.Market: 'market',
            bt.Order.Limit: 'LIMIT',
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
                   tick_interval=timedelta(seconds=1),
                   ) -> bt.Strategy:
    _logger.info("Constructing Cerebro")

    # cerebro = bt.Cerebro()
    if TRADING == 'LIVE':
        broker = store.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)
    else:
        cerebro.broker.setcash(10000.0)
    cerebro.addsizer(FullMoney)
    cerebro.addobserver(bta.observers.SLTPTracking)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addstrategy(strategy, exectype=ExecType[args.exectype])
    cerebro.broker.setcommission(leverage=1)
    cerebro.addanalyzer(RecorderAnalyzer)
    cerebro.addanalyzer(BacktraderPlottingLive, volume=True, http_port=8080, scheme=Blackly(
        hovertool_timeformat='%F %R:%S'), lookback=12000)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')

    # hist_start_date = datetime.utcnow() - timedelta(minutes=1000)
    # if strategy_class == 'SMA':
    #     hist_start_date = datetime.utcnow() - timedelta(minutes=1)
    #     dataname = "{}/{}".format(args.base, args.quote)
    #     data = store.getdata(dataname=dataname, name=dataname.replace('/', ''),
    #                          timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
    #                          # compression=60, ohlcv_limit=50, drop_newest=True, backfill_start=True)  # , historical=True)
    #                          compression=1, ohlcv_limit=50, drop_newest=True, backfill_start=True) #, historical=True)
    #
    #     cerebro.resampledata(data, timeframe=resample_timeframe, compression=resample_compression)

    if strategy_class == 'NLS1':
        hist_start_date = datetime.utcnow() - timedelta(hours=1000)
        dataname = "{}/{}".format(args.base, args.quote)
        data = store.getdata(dataname=dataname, name=dataname.replace('/', ''),
                             timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                             compression=60, ohlcv_limit=50, drop_newest=True, backfill_start=True)  # , historical=True)
        #  compression=1, ohlcv_limit=50, drop_newest=True, backfill_start=True) #, historical=True)

        cerebro.resampledata(data, timeframe=resample_timeframe, compression=resample_compression)
    else:
        # Keep hist_start_date exactly the same as max period in strategy
        hist_start_date = datetime.utcnow() - timedelta(hours=500)
        # hist_start_date = datetime.utcnow() - timedelta(minutes=2)

        # Prod
        tickers = ['BTC/USDT', 'ADA/USDT', 'ALGO/USDT', 'ATOM/USDT', 'AVAX/USDT', 'BAL/USDT', 'BAND/USDT', 'BAT/USDT', 'BCH/USDT',
                   'BLZ/USDT', 'BNB/USDT', 'BZRX/USDT', 'COMP/USDT', 'CRV/USDT', 'DASH/USDT', 'DOGE/USDT',
                   'DOT/USDT', 'EGLD/USDT', 'ENJ/USDT', 'EOS/USDT', 'ETC/USDT', 'ETH/USDT', 'FLM/USDT', 'FTM/USDT',
                   'HNT/USDT', 'ICX/USDT', 'IOST/USDT', 'IOTA/USDT', 'KAVA/USDT', 'KNC/USDT', 'LINK/USDT', 'LTC/USDT',
                   'MKR/USDT', 'NEO/USDT', 'OMG/USDT', 'ONT/USDT', 'QTUM/USDT', 'REN/USDT', 'RLC/USDT', 'RUNE/USDT', 'SNX/USDT',
                   'SOL/USDT', 'SRM/USDT', 'STORJ/USDT', 'SUSHI/USDT', 'SXP/USDT', 'THETA/USDT', 'TRB/USDT', 'TRX/USDT',
                   'UNI/USDT', 'VET/USDT', 'WAVES/USDT', 'XLM/USDT', 'XMR/USDT', 'XRP/USDT', 'XTZ/USDT', 'YFII/USDT',
                   'YFI/USDT', 'ZEC/USDT', 'ZIL/USDT', 'ZRX/USDT',
                   'TOMO/USDT', 'RSR/USDT', 'NEAR/USDT', 'MATIC/USDT',
                   'AAVE/USDT', 'FIL/USDT', 'KSM/USDT', 'LRC/USDT']
        # Last two lines aale coins were added to Binance Futures in Oct 2020
        # Test
        # tickers = ['OCEAN/USDT']
        # tickers = ['ADA/USDT', 'ALGO/USDT', 'ATOM/USDT', 'AVAX/USDT']

        # tickers = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'EOS/USDT']
        # tickers = ['BTC/USDT', 'ETH/USDT']

        for ticker in tickers:
            data = store.getdata(dataname=ticker, name=ticker.replace('/', ''),
                                 timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                                 compression=60, ohlcv_limit=50, drop_newest=True, backfill_start=True)
                                 # compression=1, ohlcv_limit=50, drop_newest=True, backfill_start=True) #, historical=True)

            cerebro.resampledata(data, timeframe=resample_timeframe, compression=resample_compression)

    res = cerebro.run()
    return cerebro, res[0]


if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True, oldbuysell=True)
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
                                        )

    else:  # Backtesting with CSV file
        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        csvpath = '{}-{}-{}.csv'.format(args.exchange, args.ticker, args.data_timeframe)
        datapath = os.path.join(modpath, 'data/{}'.format(csvpath))
        # datapath = '../fetch-historical-data'
        todate = datetime.now()
        # BTCUSDT listed on Binance
        fromdate = datetime(2017, 8, 16)
        # fromdate = datetime(todate.year-3, todate.month, todate.day)
        todate = datetime(todate.year, todate.month, todate.day)
        leverage = 1
        # Single Coin
        if strategy_class == 'NLS1':
            data = bt.feeds.MarketStore(
                symbol=f'binance_BTC-USDT',
                name=f'BTCUSDT',
                query_timeframe='1H',
                fromdate=fromdate,
                todate=todate,
                timeframe=bt.TimeFrame.Minutes,
                compression=60,
            )
            cerebro.adddata(data)

            # cerebro.resampledata(data,
            #                      timeframe=bt.TimeFrame.Minutes,
            #                      compression=60)
            # data = bt.feeds.GenericCSVData(
            #     dataname=f"{datapath}",
            #     dtformat=lambda x: format_dt_hourly(x),
            #     # dtformat=ExchangeDTFormat[args.exchange],
            #     open=ExchangeCSVIndex[args.exchange]['open'],
            #     high=ExchangeCSVIndex[args.exchange]['high'],
            #     low=ExchangeCSVIndex[args.exchange]['low'],
            #     close=ExchangeCSVIndex[args.exchange]['close'],
            #     volume=ExchangeCSVIndex[args.exchange]['volume'],
            #     fromdate=datetime(args.from_year, args.from_month, args.from_date),
            #     todate=datetime(args.to_year, args.to_month, args.to_date),
            #     timeframe=bt.TimeFrame.Minutes,
            #     compression=60,
            #     nullvalue=0.0,
            #     reverse=False)
            # cerebro.adddata(data)

            # resample_timeframes = dict(
            #     minutes=bt.TimeFrame.Minutes,
            #     daily=bt.TimeFrame.Days,
            #     weekly=bt.TimeFrame.Weeks,
            #     monthly=bt.TimeFrame.Months)

            # Use to backtest hourly timeframe on minute data
            # cerebro.resampledata(data,
            #                      timeframe=bt.TimeFrame.Minutes,
            #                      compression=60)
        # Altcoin Universe
        else:
            # New Yearly Highs
            # tickers = ['BTC-USDT', 'ETH-USDT', 'XRP-USDT', 'EOS-USDT', 'LTC-USDT', 'TRX-USDT', 'ETC-USDT', 'LINK-USDT',
            #            'XLM-USDT',
            #            'ADA-USDT',
            #            'XMR-USDT', 'DASH-USDT', 'ZEC-USDT', 'XTZ-USDT', 'BNB-USDT', 'ATOM-USDT', 'ONT-USDT', 'IOTA-USDT',
            #            'BAT-USDT',
            #            'VET-USDT',
            #            'NEO-USDT', 'QTUM-USDT', 'IOST-USDT', 'THETA-USDT', 'ALGO-USDT', 'ZIL-USDT', 'ZRX-USDT', 'OMG-USDT',
            #            'DOGE-USDT',
            #            'BAND-USDT', 'WAVES-USDT', 'ICX-USDT', 'FTM-USDT', 'ENJ-USDT', 'TOMO-USDT', 'REN-USDT']
            # CSMR Jan to Oct 2020
            tickers = ['ETH-USDT', 'BCH-USDT', 'XRP-USDT', 'EOS-USDT', 'LTC-USDT', 'TRX-USDT',
                       'ETC-USDT', 'LINK-USDT', 'XLM-USDT', 'ADA-USDT', 'XMR-USDT', 'DASH-USDT', 'ZEC-USDT',
                       'XTZ-USDT', 'BNB-USDT', 'ATOM-USDT', 'ONT-USDT', 'IOTA-USDT', 'BAT-USDT', 'VET-USDT',
                       'NEO-USDT', 'QTUM-USDT', 'IOST-USDT', 'THETA-USDT', 'ALGO-USDT', 'ZIL-USDT',
                       'KNC-USDT', 'ZRX-USDT', 'COMP-USDT', 'OMG-USDT', 'DOGE-USDT', 'SXP-USDT', 'KAVA-USDT',
                       'BAND-USDT', 'RLC-USDT', 'WAVES-USDT', 'MKR-USDT', 'SNX-USDT', 'DOT-USDT', 'YFI-USDT',
                       'BAL-USDT', 'CRV-USDT', 'TRB-USDT', 'YFII-USDT', 'RUNE-USDT', 'SUSHI-USDT', 'SRM-USDT',
                       'BZRX-USDT', 'EGLD-USDT', 'SOL-USDT', 'ICX-USDT', 'STORJ-USDT', 'BLZ-USDT', 'UNI-USDT',
                       'AVAX-USDT', 'FTM-USDT', 'ENJ-USDT', 'TOMO-USDT', 'REN-USDT']
            # Pair Trading
            # tickers = ['BTC-USDT', 'ETH-USDT']
            # tickers = ['YFI-USDT', 'YFII-USDT']
            # tickers = ['ADA-USDT', 'XLM-USDT']
            # ALT index
            # tickers = ['BCH-USDT', 'BNB-USDT', 'EOS-USDT', 'ETH-USDT', 'LTC-USDT', 'XRP-USDT', 'TRX-USDT', 'DOT-USDT', 'LINK-USDT', 'ADA-USDT']
            # tickers = ['BTC-USDT', 'ADA-USDT', 'ALGO-USDT', 'ATOM-USDT', 'AVAX-USDT', 'BAL-USDT', 'BAND-USDT',
            #            'BAT-USDT', 'BCH-USDT',
            #            'BLZ-USDT', 'BNB-USDT', 'BZRX-USDT', 'COMP-USDT', 'CRV-USDT', 'DASH-USDT', 'DOGE-USDT',
            #            'DOT-USDT', 'EGLD-USDT', 'ENJ-USDT', 'EOS-USDT', 'ETC-USDT', 'ETH-USDT', 'FLM-USDT', 'FTM-USDT',
            #            'HNT-USDT', 'ICX-USDT', 'IOST-USDT', 'IOTA-USDT', 'KAVA-USDT', 'KNC-USDT', 'LINK-USDT',
            #            'LTC-USDT',
            #            'MKR-USDT', 'NEO-USDT', 'OMG-USDT', 'ONT-USDT', 'QTUM-USDT', 'REN-USDT', 'RLC-USDT', 'RUNE-USDT',
            #            'SNX-USDT',
            #            'SOL-USDT', 'SRM-USDT', 'STORJ-USDT', 'SUSHI-USDT', 'SXP-USDT', 'THETA-USDT', 'TRB-USDT',
            #            'TRX-USDT',
            #            'UNI-USDT', 'VET-USDT', 'WAVES-USDT', 'XLM-USDT', 'XMR-USDT', 'XRP-USDT', 'XTZ-USDT',
            #            'YFII-USDT',
            #            'YFI-USDT', 'ZEC-USDT', 'ZIL-USDT', 'ZRX-USDT']
                       # 'TOMO-USDT', 'RSR-USDT', 'NEAR-USDT', 'MATIC-USDT',
                       # 'AAVE-USDT', 'FIL-USDT', 'KSM-USDT', 'LRC-USDT']
            # tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT']
            # No volatility
            # 178% 53 60 coins max 8 positions
            # 164% 51 60 coins max 12 positions
            # 137% 45 60 coins max 15 positions
            # 123% 40 60 coins max 20 positions
            # With volatility
            # 215% 18 60 coins max 35 positions & stdev 100
            # 198% 18 60 coins max 35 positions & stdev 50
            # 165% 19 60 coins max 35 positions & stdev 20
            # 138% 18.4 60 coins max 35 positions & stdev 10
            # 113% 18.4 60 coins max 35 positions
            # 82% 24 60 coins max 30 positions
            # 68% 29 60 coins max 25 positions
            # 36% 35 60 coins max 20 positions
            # -41% 64 60 coins max 10 positions
            # -77% 35 60 coins max 8 positions

                        # ,'KSMUSDT', 'RSRUSDT', 'LRCUSDT']
            # tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT']
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
                data = bt.feeds.MarketStore(
                    symbol=f'binance_{ticker}',
                    name=f'{ticker}',
                    query_timeframe='1Min',
                    timeframe=bt.TimeFrame.Minutes,
                    fromdate=fromdate,
                    todate=todate,
                    compression=1,
                )
                # cerebro.adddata(data)

                cerebro.resampledata(data,
                                     timeframe=bt.TimeFrame.Minutes,
                                     compression=60)
        cerebro.broker.set_coc(False)
        cerebro.broker.setcash(10000.0)
        # 627 21 - 1 pct change period
        # 3121 18 - 2
        # 2439 18 - 3
        # 1684 19 - 4
        # 1214 24 - 5
        # 1060 21 - 10
        # 3224 16
        cerebro.addsizer(FullMoney)
        cerebro.broker.setcommission(commission=0.00036, leverage=leverage)
        print('Starting {}'.format(args.strategy))
        cerebro.addobserver(bta.observers.SLTPTracking)
        cerebro.addobserver(bt.observers.DrawDown)
        cerebro.addstrategy(strategy, exectype=ExecType[args.exectype])
        # strats = cerebro.optstrategy(
        #     strategy,
        #     order_target_percent=range(2, 5))

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    addAnalyzers(cerebro)

    stats = cerebro.run(maxcpus=16)
    stat = stats[0].analyzers

    print(args.strategy)
    print('======== PERFORMANCE ========\n')
    print('{}x leverage'.format(leverage))
    print(
        '{}, {}'.format(fromdate.date(), todate.date()))
    getAnalysis(stat)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    if args.plot == True:
        p = BacktraderPlotting(style='candle', scheme=Blackly())
        cerebro.plot(p)
