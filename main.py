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


if ENV == PRODUCTION:  # Live trading with Binance
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
    cerebro.addstrategy(Strategy[args.strategy], exectype=ExecType[args.exectype])

    cerebro.addanalyzer(RecorderAnalyzer)
    cerebro.addanalyzer(BacktraderPlottingLive, volume=True, scheme=Blackly(
        hovertool_timeformat='%F %R:%S'), lookback=12000)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    
    # hist_start_date = datetime.utcnow() - timedelta(hours=1000)
    hist_start_date = datetime.utcnow() - timedelta(minutes=1000)
    dataname="{}/{}".format(args.base, args.quote)
    data = store.getdata(dataname=dataname, name=dataname.replace('/', ''),
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                    #  compression=60, ohlcv_limit=50, drop_newest=True, backfill_start=True) #, historical=True)
                     compression=1, ohlcv_limit=50, drop_newest=True, backfill_start=True) #, historical=True)

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
                                        # data_compression=60,
                                        data_compression=1,
                                        resample_timeframe=bt.TimeFrame.Minutes,
                                        # resample_compression=60,
                                        resample_compression=1,
                                        runtime_seconds=60000,
                                        tick_interval=timedelta(seconds=60),
                                        start_delays=[None, None],
                                        num_gen_bars=[0, 10],
                                        num_data=2,
                                        )

    else:  # Backtesting with CSV file
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
                            compression=60)
                            #  compression=720)

        cerebro.broker.setcash(10000.0)
        cerebro.addsizer(FullMoney)
        cerebro.broker.setcommission(commission=0.0006)
        print('Starting {}'.format(args.strategy))
        cerebro.addobserver(bta.observers.SLTPTracking)
        cerebro.addstrategy(Strategy[args.strategy], exectype=ExecType[args.exectype])

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    addAnalyzers(cerebro)

    stats = cerebro.run(**eval('dict(' + args.cerebro + ')'))
    stat = stats[0].analyzers
    
    print(args.strategy)
    print('======== PERFORMANCE ========\n')
    print('{}'.format(csvpath))
    print('{}, {}, {} to {}, {}, {}'.format(args.from_year, args.from_month, args.from_date, args.to_year, args.to_month, args.to_date))
    getAnalysis(stat)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    if args.plot:
        p = BacktraderPlotting(style='candle', scheme=Blackly())
        cerebro.plot(p)
