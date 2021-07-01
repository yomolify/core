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
import concurrent.futures
# TODO - why is backtest not entering bitcoin?
# TODO - Make add_order work with both size and target
# TODO - single command that runs get_wallet_balance, marketstore and core
# TODO - https://community.backtrader.com/topic/2153/backtrader-with-a-lot-of-datafeed-trick-to-reduce-data-loading-time
# TODO - https://community.backtrader.com/topic/2240/how-to-speed-up-almost-100-times-when-add-data-and-preload-data
# TODO - copy over strategy.py, ccxtbroker.py and ccxtstore.py and ccxtfeed.py to aws
# TODO - test new yearly highs using batch orders and marketstore
from config import BINANCE, ENV, PRODUCTION, BASE, QUOTE, DEBUG, TRADING

if ENV == PRODUCTION:
    from ccxtbt import CCXTStore

import backtrader as bt
import backtrader_addons as bta
from analyzers import *
from btplotting import BacktraderPlotting, BacktraderPlottingLive
from btplotting.schemes import Blackly, Tradimo
from btplotting.analyzers import RecorderAnalyzer
from threading import Thread, Event

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

    config = {'apiKey': params["binance"]["apikey"],
              'secret': params["binance"]["secret"],
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
            'filled_order': {
                'key': 'status',
                'value': 'filled'
            },
            'canceled_order': {
                'key': 'status',
                'value': 'canceled'}
        }
    }

if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True, oldbuysell=True)
    warnings.filterwarnings("ignore")
    print("Running in {} and {} trading".format(ENV, TRADING))

    if ENV == PRODUCTION:  # Live trading with Binance
        if TRADING == 'LIVE':
            broker = store.getbroker(broker_mapping=broker_mapping)
            cerebro.setbroker(broker)
        else:
            cerebro.broker.setcash(10000.0)
        cerebro.addsizer(FullMoney)
        cerebro.addstrategy(strategy, exectype=ExecType[args.exectype])
        cerebro.broker.setcommission(leverage=3)
        if strategy_class == 'NewYearlyHighs' or strategy_class == 'SMA' or strategy_class == 'TestSMA':
            tickers = ['BTC/USDT', 'ADA/USDT', 'ALGO/USDT']
            # tickers = ['BTC/USDT', 'ADA/USDT', 'ALGO/USDT', 'ATOM/USDT', 'AVAX/USDT', 'BAL/USDT', 'BAND/USDT',
            #            'BAT/USDT',
            #            'BCH/USDT',
            #            'BLZ/USDT', 'BNB/USDT', 'BZRX/USDT', 'COMP/USDT', 'CRV/USDT', 'DASH/USDT', 'DOGE/USDT',
            #            'DOT/USDT', 'EGLD/USDT', 'ENJ/USDT', 'EOS/USDT', 'ETC/USDT', 'ETH/USDT', 'FLM/USDT', 'FTM/USDT',
            #            'HNT/USDT', 'ICX/USDT', 'IOST/USDT', 'IOTA/USDT', 'KAVA/USDT', 'KNC/USDT', 'LINK/USDT',
            #            'LTC/USDT',
            #            'MKR/USDT', 'NEO/USDT', 'OMG/USDT', 'ONT/USDT', 'QTUM/USDT', 'REN/USDT', 'RLC/USDT', 'RUNE/USDT',
            #            'SNX/USDT',
            #            'SOL/USDT', 'SRM/USDT', 'STORJ/USDT', 'SUSHI/USDT', 'SXP/USDT', 'THETA/USDT', 'TRB/USDT',
            #            'TRX/USDT',
            #            'UNI/USDT', 'VET/USDT', 'WAVES/USDT', 'XLM/USDT', 'XMR/USDT', 'XRP/USDT', 'XTZ/USDT',
            #            'YFII/USDT',
            #            'YFI/USDT', 'ZEC/USDT', 'ZIL/USDT', 'ZRX/USDT',
            #            'TOMO/USDT', 'RSR/USDT', 'NEAR/USDT', 'MATIC/USDT',
            #            'AAVE/USDT', 'FIL/USDT', 'KSM/USDT', 'LRC/USDT', 'OCEAN/USDT', 'AXS/USDT', 'ZEN/USDT',
            #            'ALPHA/USDT',
            #            'CTK/USDT', 'BEL/USDT', 'CVC/USDT', 'DEFI/USDT', 'SKL/USDT', 'GRT/USDT', '1INCH/USDT']
            # new coins
            # CHZ / USDT
            # SAND / USDT
            # ANKR / USDT
            # LUNA / USD
            # AKRO/USDT
            # hist_start_date = datetime.utcnow() - timedelta(hours=501)
            hist_start_date = datetime.utcnow() - timedelta(minutes=1)
            for ticker in tickers:
                data = store.getdata(dataname=ticker, name=ticker,
                                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                                     compression=1, ohlcv_limit=50, drop_newest=True)  # , historical=True)
                # data = store.getdata(dataname=ticker, name=ticker,
                #                      fromdate=hist_start_date,
                #                      tf='1Min')

                cerebro.adddata(data)
        cerebro.run()
    else:  # Backtesting with CSV file
        # datapath = '../fetch-historical-data'
        #
        # Benchmark backtest
        # todate = datetime.now()
        todate = datetime(2021, 6, 20)
        fromdate = datetime(2021, 6, 10)

        todate = datetime(2021, 6, 10)
        fromdate = datetime(2021, 6, 1)

        todate = datetime(2021, 5, 10)
        fromdate = datetime(2021, 5, 1)

        todate = datetime(2021, 6, 1)
        fromdate = datetime(2021, 4, 1)

        todate = datetime(2021, 7, 1)
        fromdate = datetime(2021, 1, 1)

        todate = datetime(2021, 7, 1)
        fromdate = datetime(2021, 6, 1)
        # todate = datetime(2021, 4, 5)
        # todate = datetime(2021, 6, 20)
        # fromdate = datetime(2019, 11, 1)
        # fromdate = datetime(2020, 1, 1)
        # fromdate = datetime(2020, 12, 1)
        # fromdate = datetime(2021, 1, 27)
        # fromdate = datetime(2021, 6, 15)
        # fromdate = datetime(2020, 8, 1)
        # fromdate = datetime(2020, 12, 1)
        # fromdate = datetime(2021, 2, 1)
        # fromdate = datetime(2021, 1, 1)
        # fromdate = datetime(2021, 1, 1)
        #
        # todate = datetime(2021, 3, 14)

        # Recent
        # fromdate = datetime(2020, 11, 14)
        # BTCUSDT listed on Binance
        # fromdate = datetime(2017, 8, 16)
        # fromdate = datetime(todate.year-1, todate.month, todate.day-16)
        # fromdate = datetime(2020, 10, 14)
        # fromdate = datetime(todate.year, todate.month - 1, todate.day)
        # todate = datetime(todate.year, todate.month, todate.day)
        # fromdate = datetime(2019, 11, 14)
        # todate = datetime(2020, 11, 28)
        #
        # fromdate = datetime(args.from_year, args.from_month, args.from_date)
        # todate = datetime(args.to_year, args.to_month, args.to_date)
        leverage = 1
        # 80 and 15 on 1x
        # Single Coin
        if strategy_class == 'xNLS1':
            leverage = 1
            # data = bt.feeds.MarketStore(
            #     symbol=f'binance_BTC-USDT',
            #     name=f'BTCUSDT',
            #     query_timeframe='1H',
            #     fromdate=fromdate,
            #     todate=todate,
            #     timeframe=bt.TimeFrame.Minutes,
            #     compression=60,
            # )
            # cerebro.adddata(data)
            #
            # cerebro.resampledata(data,
            #                      timeframe=bt.TimeFrame.Minutes,
            #                      compression=60)
            #

            modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
            csvpath = '{}-{}-{}.csv'.format(args.exchange, args.ticker, args.data_timeframe)
            # csvpath = f'{}{}.csv'.format(args.exchange, args.ticker, args.data_timeframe)
            csvpath = 'ethusd.csv'
            datapath = os.path.join(modpath, 'data/{}'.format(csvpath))
            # datapath = os.path.join(modpath, '../cryptocurrency-historical-data-master/data/{}'.format(csvpath))

            data = bt.feeds.GenericCSVData(
                dataname=datapath,
                # dtformat=ExchangeDTFormat[args.exchange],
                dtformat=ExchangeDTFormat['bitfinex'],
                open=ExchangeCSVIndex[args.exchange]['open'],
                high=ExchangeCSVIndex[args.exchange]['high'],
                low=ExchangeCSVIndex[args.exchange]['low'],
                close=ExchangeCSVIndex[args.exchange]['close'],
                volume=ExchangeCSVIndex[args.exchange]['volume'],
                fromdate=datetime(args.from_year, args.from_month, args.from_date),
                todate=datetime(args.to_year, args.to_month, args.to_date),
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
                                 compression=5)
        # Altcoin Universe
        else:
            # New Yearly Highs
            if strategy_class == 'GCSImproved' or 'NewYearlyHighs' or 'NewYearlyHighsStops' or "HMA" or "SHA" or "NLS1" or "GoldenCrossStops" or "LS" or "LS5Min" or "NewYearlyHighsImproved" or "SwingHL" or "EE" or "TurtleTrader" or 'CrossSectional' or 'VWAP' or 'Trend' in args.strategy:
                tickers = ['BTC-USDT', 'ETH-USDT', 'XRP-USDT', 'EOS-USDT', 'LTC-USDT', 'TRX-USDT', 'ETC-USDT',
                           'LINK-USDT',
                           'XLM-USDT',
                           'ADA-USDT',
                           'XMR-USDT', 'DASH-USDT',
                           'ZEC-USDT', 'XTZ-USDT', 'BNB-USDT', 'ATOM-USDT', 'ONT-USDT', 'IOTA-USDT',
                           'BAT-USDT',
                           'VET-USDT',
                           'NEO-USDT', 'QTUM-USDT', 'IOST-USDT', 'THETA-USDT', 'ALGO-USDT', 'ZIL-USDT', 'ZRX-USDT', 'OMG-USDT',
                           'DOGE-USDT',
                           'BAND-USDT', 'WAVES-USDT', 'ICX-USDT', 'FTM-USDT', 'ENJ-USDT', 'TOMO-USDT', 'REN-USDT']
                # tickers = ['BTC-USDT', 'ETH-USDT', 'XRP-USDT', 'EOS-USDT', 'LTC-USDT', 'TRX-USDT', 'ETC-USDT',
                #            'LINK-USDT',
                #             'XLM-USDT',
                #            'ADA-USDT',
                #            'XMR-USDT', 'DASH-USDT', 'ZEC-USDT', 'XTZ-USDT', 'BNB-USDT', 'ATOM-USDT', 'ONT-USDT', 'IOTA-USDT',
                #            'BAT-USDT',
                #            'VET-USDT',
                #            'NEO-USDT', 'QTUM-USDT', 'IOST-USDT', 'THETA-USDT', 'ALGO-USDT', 'ZIL-USDT', 'ZRX-USDT', 'OMG-USDT',
                #            'DOGE-USDT',
                #            'BAND-USDT', 'WAVES-USDT', 'ICX-USDT', 'FTM-USDT', 'ENJ-USDT', 'TOMO-USDT', 'REN-USDT']
                # tickers = ['BTC-USDT', 'ADA-USDT', 'ALGO-USDT', 'ATOM-USDT', 'AVAX-USDT', 'BAL-USDT', 'BAND-USDT',
                #           'BAT-USDT',
                #           'BCH-USDT',
                #           'BLZ-USDT', 'BNB-USDT', 'BZRX-USDT', 'COMP-USDT', 'CRV-USDT', 'DASH-USDT', 'DOGE-USDT',
                #           'DOT-USDT', 'EGLD-USDT', 'ENJ-USDT', 'EOS-USDT', 'ETC-USDT', 'ETH-USDT', 'FLM-USDT', 'FTM-USDT',
                #           'HNT-USDT', 'ICX-USDT', 'IOST-USDT', 'IOTA-USDT', 'KAVA-USDT', 'KNC-USDT', 'LINK-USDT',
                #           'LTC-USDT',
                #           'MKR-USDT', 'NEO-USDT', 'OMG-USDT', 'ONT-USDT', 'QTUM-USDT', 'REN-USDT', 'RLC-USDT', 'RUNE-USDT',
                #           'SNX-USDT',
                #           'SOL-USDT', 'SRM-USDT', 'STORJ-USDT', 'SUSHI-USDT', 'SXP-USDT', 'THETA-USDT', 'TRB-USDT',
                #           'TRX-USDT',
                #           'UNI-USDT', 'VET-USDT', 'WAVES-USDT', 'XLM-USDT', 'XMR-USDT', 'XRP-USDT', 'XTZ-USDT',
                #           'YFII-USDT',
                #           'YFI-USDT', 'ZEC-USDT', 'ZIL-USDT', 'ZRX-USDT',
                #           'TOMO-USDT', 'RSR-USDT', 'NEAR-USDT', 'MATIC-USDT',
                #           'AAVE-USDT', 'FIL-USDT', 'KSM-USDT', 'LRC-USDT', 'OCEAN-USDT', 'AXS-USDT', 'ZEN-USDT',
                #           'ALPHA-USDT',
                #           'CTK-USDT', 'BEL-USDT', 'CVC-USDT', 'DEFI-USDT', 'SKL-USDT', 'GRT-USDT', '1INCH-USDT']
                # All Spot USDT pairs
                # Stables + LVTs
                # 'TUSD-USDT','PAX-USDT''USDC-USDT', , 'BUSD-USDT' 'BTCUP-USDT', 'BTCDOWN-USDT', 'ETHUP-USDT', 'ETHDOWN-USDT',, 'ADAUP-USDT', 'ADADOWN-USDT', 'LINKUP-USDT', 'LINKDOWN-USDT, 'BNBUP-USDT', 'BNBDOWN-USDT',
                # tickers = ['BTC-USDT', 'ETH-USDT', 'BNB-USDT', 'NEO-USDT', 'LTC-USDT', 'QTUM-USDT', 'ADA-USDT', 'XRP-USDT',
                #            'EOS-USDT', 'IOTA-USDT', 'XLM-USDT', 'ONT-USDT', 'TRX-USDT', 'ETC-USDT', 'ICX-USDT', 'NULS-USDT',
                #            'VET-USDT', 'BCH-USDT', 'LINK-USDT', 'WAVES-USDT', 'BTT-USDT', 'ONG-USDT', 'HOT-USDT', 'ZIL-USDT',
                #            'ZRX-USDT', 'FET-USDT', 'BAT-USDT', 'XMR-USDT', 'ZEC-USDT', 'IOST-USDT', 'CELR-USDT', 'DASH-USDT',
                #            'NANO-USDT', 'OMG-USDT', 'THETA-USDT', 'ENJ-USDT', 'MITH-USDT', 'MATIC-USDT', 'ATOM-USDT', 'TFUEL-USDT',
                #            'ONE-USDT', 'FTM-USDT', 'ALGO-USDT', 'GTO-USDT', 'DOGE-USDT', 'DUSK-USDT', 'ANKR-USDT', 'WIN-USDT',
                #            'COS-USDT', 'COCOS-USDT', 'MTL-USDT', 'TOMO-USDT', 'PERL-USDT', 'DENT-USDT', 'MFT-USDT', 'KEY-USDT',
                #            'DOCK-USDT', 'WAN-USDT', 'FUN-USDT', 'CVC-USDT', 'CHZ-USDT', 'BAND-USDT', 'BEAM-USDT', 'XTZ-USDT', 'REN-USDT',
                #            'RVN-USDT', 'HBAR-USDT', 'NKN-USDT', 'STX-USDT', 'KAVA-USDT', 'ARPA-USDT', 'IOTX-USDT', 'RLC-USDT',
                #            'CTXC-USDT', 'TROY-USDT', 'VITE-USDT', 'FTT-USDT', 'EUR-USDT', 'OGN-USDT', 'DREP-USDT', 'TCT-USDT',
                #            'WRX-USDT', 'BTS-USDT', 'LSK-USDT', 'BNT-USDT', 'LTO-USDT', 'AION-USDT', 'MBL-USDT', 'COTI-USDT', 'STPT-USDT',
                #            'WTC-USDT', 'DATA-USDT', 'SOL-USDT', 'CTSI-USDT', 'HIVE-USDT', 'CHR-USDT',  'GXS-USDT', 'ARDR-USDT',
                #            'MDT-USDT', 'STMX-USDT', 'KNC-USDT', 'REP-USDT', 'LRC-USDT', 'PNT-USDT', 'COMP-USDT', 'SC-USDT', 'ZEN-USDT', 'SNX-USDT']
                           # 'VTHO-USDT', 'DGB-USDT', 'GBP-USDT', 'SXP-USDT', 'MKR-USDT', 'DCR-USDT', 'STORJ-USDT', 'XTZUP-USDT', 'XTZDOWN-USDT', 'MANA-USDT', 'AUD-USDT', 'YFI-USDT', 'BAL-USDT', 'BLZ-USDT', 'IRIS-USDT', 'KMD-USDT', 'JST-USDT', 'SRM-USDT', 'ANT-USDT', 'CRV-USDT', 'SAND-USDT', 'OCEAN-USDT', 'NMR-USDT', 'DOT-USDT', 'LUNA-USDT', 'RSR-USDT', 'PAXG-USDT', 'WNXM-USDT', 'TRB-USDT', 'BZRX-USDT', 'SUSHI-USDT', 'YFII-USDT', 'KSM-USDT', 'EGLD-USDT', 'DIA-USDT', 'RUNE-USDT', 'FIO-USDT', 'UMA-USDT', 'EOSUP-USDT', 'EOSDOWN-USDT', 'TRXUP-USDT', 'TRXDOWN-USDT', 'XRPUP-USDT', 'XRPDOWN-USDT', 'DOTUP-USDT', 'DOTDOWN-USDT', 'BEL-USDT', 'WING-USDT', 'LTCUP-USDT', 'LTCDOWN-USDT', 'UNI-USDT', 'NBS-USDT', 'OXT-USDT', 'AVAX-USDT', 'HNT-USDT', 'FLM-USDT', 'UNIUP-USDT', 'UNIDOWN-USDT', 'ORN-USDT', 'UTK-USDT', 'XVS-USDT', 'ALPHA-USDT', 'AAVE-USDT', 'NEAR-USDT', 'SXPUP-USDT', 'SXPDOWN-USDT', 'FIL-USDT', 'FILUP-USDT', 'FILDOWN-USDT', 'YFIUP-USDT', 'YFIDOWN-USDT', 'INJ-USDT', 'AUDIO-USDT', 'CTK-USDT', 'BCHUP-USDT', 'BCHDOWN-USDT', 'AKRO-USDT', 'AXS-USDT', 'HARD-USDT', 'DNT-USDT', 'STRAX-USDT', 'UNFI-USDT', 'ROSE-USDT', 'AVA-USDT', 'XEM-USDT', 'AAVEUP-USDT', 'AAVEDOWN-USDT', 'SKL-USDT', 'SUSD-USDT', 'SUSHIUP-USDT', 'SUSHIDOWN-USDT', 'XLMUP-USDT', 'XLMDOWN-USDT', 'GRT-USDT', 'JUV-USDT', 'PSG-USDT', '1INCH-USDT', 'REEF-USDT', 'OG-USDT', 'ATM-USDT', 'ASR-USDT', 'CELO-USDT', 'RIF-USDT', 'BTCST-USDT', 'TRU-USDT', 'CKB-USDT', 'TWT-USDT', 'FIRO-USDT', 'LIT-USDT', 'SFP-USDT', 'DODO-USDT', 'CAKE-USDT', 'ACM-USDT', 'BADGER-USDT', 'FIS-USDT', 'OM-USDT', 'POND-USDT', 'DEGO-USDT', 'ALICE-USDT', 'LINA-USDT', 'PERP-USDT', 'RAMP-USDT', 'SUPER-USDT', 'CFX-USDT', 'EPS-USDT', 'AUTO-USDT', 'TKO-USDT', 'PUNDIX-USDT', 'TLM-USDT', '1INCHUP-USDT', '1INCHDOWN-USDT', 'BTG-USDT', 'MIR-USDT', 'BAR-USDT', 'FORTH-USDT', 'BAKE-USDT', 'BURGER-USDT', 'SLP-USDT', 'SHIB-USDT', 'ICP-USDT', 'AR-USDT', 'POLS-USDT', 'MDX-USDT', 'MASK-USDT', 'LPT-USDT', 'NU-USDT', 'XVG-USDT', 'ATA-USDT', 'GTC-USDT', 'TORN-USDT']
                # tickers = ['BAND-USDT', 'AAVE-USDT', 'FTM-USDT', 'DOGE-USDT', 'FIL-USDT', 'KSM-USDT',
                #           'ALPHA-USDT']
                # tickers = ['BTC-USDT', 'ETH-USDT', 'XRP-USDT', 'EOS-USDT', 'LTC-USDT', 'TRX-USDT', 'ETC-USDT',
                # 'LINK-USDT']
                # tickers = ['MKR-USDT', 'ETH-USDT', 'BNB-USDT']
                    #
                # tickers = ['ETH-USDT']
                tickers = ['BNB-USDT']
                # tickers = ['LTC-USDT']
                # tickers = ['AAVE-USDT']
                # tickers = ['BTC-USDT', 'ETH-USDT', 'XRP-USDT']
                # tickers = ['AAVE-USDT']
                # tickers = ['FIL-USDT']

                # tickers = ['LTC-USDT']
                # tickers = ['DOT-USDT']
                # tickers = ['BTC-USDT']
                # tickers = ['BTC-USDT', 'ADA-USDT', 'ALGO-USDT', 'ATOM-USDT', 'AVAX-USDT', 'BAL-USDT', 'BAND-USDT',
                #            'BAT-USDT',
                #            'BCH-USDT',
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
                #            'YFI-USDT', 'ZEC-USDT', 'ZIL-USDT', 'ZRX-USDT',
                #            'TOMO-USDT', 'RSR-USDT', 'NEAR-USDT', 'MATIC-USDT',
                #            'AAVE-USDT', 'FIL-USDT', 'KSM-USDT', 'LRC-USDT', 'OCEAN-USDT', 'AXS-USDT', 'ZEN-USDT',
                #            'ALPHA-USDT',
                #            'CTK-USDT', 'BEL-USDT', 'CVC-USDT']
                # tickers = ['BTC-USDT', 'SXP-USDT']
                # tickers = ['BTC-USDT', 'ETH-USDT', 'XRP-USDT']
                # tickers = ['BTC-USDT', 'ADA-USDT', 'ALGO-USDT', 'ATOM-USDT', 'AVAX-USDT', 'BAL-USDT', 'BAND-USDT',
                #            'BAT-USDT',
                #            'BCH-USDT',
                #            'BLZ-USDT', 'BNB-USDT', 'BZRX-USDT', 'COMP-USDT', 'CRV-USDT', 'DASH-USDT', 'DOGE-USDT',
                #            'DOT-USDT', 'EGLD-USDT', 'ENJ-USDT', 'EOS-USDT', 'ETC-USDT', 'ETH-USDT', 'FLM-USDT',
                #            'FTM-USDT',
                #            'HNT-USDT', 'ICX-USDT', 'IOST-USDT', 'IOTA-USDT', 'KAVA-USDT', 'KNC-USDT', 'LINK-USDT',
                #            'LTC-USDT',
                #            'MKR-USDT', 'NEO-USDT', 'OMG-USDT', 'ONT-USDT', 'QTUM-USDT', 'REN-USDT', 'RLC-USDT',
                #            'RUNE-USDT',
                #            'SNX-USDT',
                #            'SOL-USDT', 'SRM-USDT', 'STORJ-USDT', 'SUSHI-USDT', 'SXP-USDT', 'THETA-USDT', 'TRB-USDT',
                #            'TRX-USDT',
                #            'UNI-USDT', 'VET-USDT', 'WAVES-USDT', 'XLM-USDT', 'XMR-USDT', 'XRP-USDT', 'XTZ-USDT',
                #            'YFII-USDT',
                #            'YFI-USDT', 'ZEC-USDT', 'ZIL-USDT', 'ZRX-USDT',
                #            'TOMO-USDT', 'RSR-USDT', 'NEAR-USDT', 'MATIC-USDT',
                #            'AAVE-USDT', 'FIL-USDT', 'KSM-USDT', 'LRC-USDT']
                cerebro.broker.setcash(10000.0)

            # CSMR Jan to Oct 2020
            # if strategy_class == 'CrossSectional' or 'CrossSectionalImproved':
            #     tickers = ['ETH-USDT', 'BCH-USDT', 'XRP-USDT', 'EOS-USDT', 'LTC-USDT', 'TRX-USDT',
            #                'ETC-USDT', 'LINK-USDT', 'XLM-USDT', 'ADA-USDT', 'XMR-USDT', 'DASH-USDT', 'ZEC-USDT',
            #                'XTZ-USDT', 'BNB-USDT', 'ATOM-USDT', 'ONT-USDT', 'IOTA-USDT', 'BAT-USDT', 'VET-USDT',
            #                'NEO-USDT', 'QTUM-USDT', 'IOST-USDT', 'THETA-USDT', 'ALGO-USDT', 'ZIL-USDT',
            #                'KNC-USDT', 'ZRX-USDT', 'COMP-USDT', 'OMG-USDT', 'DOGE-USDT', 'SXP-USDT', 'KAVA-USDT',
            #                'BAND-USDT', 'RLC-USDT', 'WAVES-USDT', 'MKR-USDT', 'SNX-USDT', 'DOT-USDT', 'YFI-USDT',
            #                'BAL-USDT', 'CRV-USDT', 'TRB-USDT', 'YFII-USDT', 'RUNE-USDT', 'SUSHI-USDT', 'SRM-USDT',
            #                'BZRX-USDT', 'EGLD-USDT', 'SOL-USDT', 'ICX-USDT', 'STORJ-USDT', 'BLZ-USDT', 'UNI-USDT',
            #                'AVAX-USDT', 'FTM-USDT', 'ENJ-USDT', 'TOMO-USDT', 'REN-USDT']
            if strategy_class == 'BTCEMA':
                tickers = ['ETH-BTC', 'LTC-BTC', 'BNB-BTC', 'XRP-BTC', 'BCH-BTC', 'LINK-BTC', 'DOT-BTC', 'ADA-BTC', 'XLM-BTC', 'XMR-BTC', 'TRX-BTC', 'XTZ-BTC', 'XEM-BTC', 'NEO-BTC', 'DASH-BTC', 'ATOM-BTC', 'VET-BTC', 'WAVES-BTC', 'IOTA-BTC', 'ALGO-BTC', 'ETC-BTC', 'THETA-BTC', 'ZIL-BTC', 'MKR-BTC', 'OMG-BTC']

                    # , 'DCR-BTC', 'BAT-BTC', 'ZRX-BTC', 'REN-BTC', 'QTUM-BTC', 'KNC-BTC', 'LRC-BTC', 'REP-BTC', 'ICX-BTC', 'TFUEL-BTC', 'IOST-BTC', 'FTM-BTC', 'LTO-BTC', 'DUSK-BTC', 'COTI-BTC', 'AAVE-BTC']
                cerebro.broker.setcash(1.0)

                # tickers = ['ETH-USDT', 'LTC-USDT', 'BNB-USDT', 'XRP-USDT', 'BCH-USDT', 'LINK-USDT', 'DOT-USDT', 'ADA-USDT', 'XLM-USDT', 'XMR-USDT', 'TRX-USDT', 'XTZ-USDT', 'XEM-USDT', 'NEO-USDT', 'DASH-USDT', 'ATOM-USDT', 'VET-USDT', 'WAVES-USDT', 'IOTA-USDT', 'ALGO-USDT', 'ETC-USDT', 'THETA-USDT', 'ZIL-USDT', 'MKR-USDT', 'OMG-USDT', 'DCR-USDT', 'BAT-USDT', 'ZRX-USDT', 'REN-USDT', 'QTUM-USDT', 'KNC-USDT', 'LRC-USDT', 'REP-USDT', 'ICX-USDT', 'TFUEL-USDT', 'IOST-USDT', 'FTM-USDT', 'LTO-USDT', 'DUSK-USDT', 'COTI-USDT', 'AAVE-USDT']
            # tickers = ['ETH-BTC']

            # Pair Trading
            # tickers = ['BTC-USDT']
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
                    symbol=f'binancefutures_{ticker}',
                    # symbol=f'binance_{ticker}',
                    name=f'{ticker}',
                    # query_timeframe='1Min',
                    # query_timeframe='1H',
                    query_timeframe='5Min',
                    # timeframe=bt.TimeFrame.Minutes,
                    fromdate=fromdate,
                    todate=todate,
                    # compression=1,
                    # compression=60,
                )

                cerebro.adddata(data, name=f'5m_{ticker}')
                # cerebro.resampledata(data,
                #                                           timeframe=bt.TimeFrame.Minutes,
                #                                           compression=60, name=f'hourly_{ticker}')
            for ticker in tickers:
                data = bt.feeds.MarketStore(
                    symbol=f'binancefutures_{ticker}',
                    # symbol=f'binance_{ticker}',
                    name=f'{ticker}',
                    # query_timeframe='5Min',
                    # query_timeframe='5Min',
                    query_timeframe='1H',
                    fromdate=fromdate,
                    todate=todate,
                )
                # cerebro.resampledata(data,
                #                                           timeframe=bt.TimeFrame.Minutes,
                #                                           compression=480)
                cerebro.adddata(data, name=f'1H_{ticker}')

            # add btc dominance data to cerebro
            # btc_dom = bt.feeds.GenericCSVData(
            #
            # )

            # To add Heikin Ashi data source
            # for ticker in tickers:
            #     ha_data = bt.feeds.MarketStore(
            #         # symbol=f'binancefutures_{ticker}',
            #         symbol=f'binance_{ticker}',
            #         name=f'{ticker}',
            #         # query_timeframe='1Min',
            #         query_timeframe='1H',
            #         # timeframe=bt.TimeFrame.Minutes,
            #         fromdate=fromdate,
            #         todate=todate,
            #         # compression=1,
            #         # compression=60,
            #     )
            #     ha_data.addfilter(bt.filters.HeikinAshi(ha_data))
            #     cerebro.adddata(ha_data, name=f'Heikin_{ticker}')

                # cerebro.resampledata(data,
                #                      timeframe=bt.TimeFrame.Minutes,
                #                      compression=60)
        cerebro.broker.set_coc(False)
        # 627 21 - 1 pct change period
        # 3121 18 - 2
        # 2439 18 - 3
        # 1684 19 - 4
        # 1214 24 - 5
        # 1060 21 - 10
        # 3224 16
        cerebro.addsizer(FullMoney)
        cerebro.broker.setcommission(commission=0.0004, leverage=leverage)
        # cerebro.broker.setcommission(commission=0.00075, leverage=leverage)
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
