#!/usr/bin/env python3

import time
import backtrader as bt
import datetime as dt

from ccxtbt import CCXTStore
from config import BINANCE, ENV, PRODUCTION, COIN_TARGET, COIN_REFER, DEBUG

from dataset.dataset import CustomDataset
from sizer.percent import FullMoney
from strategies.basic_rsi import BasicRSI
from strategies.L1 import L1
from utils import print_trade_analysis, print_sqn, send_telegram_message
from backtrader_plotting import Bokeh, OptBrowser
from backtrader_plotting.schemes import Tradimo

def main():
    cerebro = bt.Cerebro(quicknotify=True)

    if ENV == PRODUCTION:  # Live trading with Binance
        broker_config = {
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret"),
            'nonce': lambda: str(int(time.time() * 1000)),
            'enableRateLimit': True,
        }

        store = CCXTStore(exchange='binance', currency=COIN_REFER, config=broker_config, retries=5, debug=DEBUG)

        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.Stop: 'stop-loss',
                bt.Order.StopLimit: 'stop limit'
            },
            'mappings': {
                'closed_order': {
                    'key': 'status',
                    'value': 'closed'
                },
                'canceled_order': {
                    'key': 'status',
                    'value': 'canceled'
                }
            }
        }

        broker = store.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)

        hist_start_date = dt.datetime.utcnow() - dt.timedelta(minutes=30000)
        data = store.getdata(
            dataname='%s/%s' % (COIN_TARGET, COIN_REFER),
            name='%s%s' % (COIN_TARGET, COIN_REFER),
            timeframe=bt.TimeFrame.Minutes,
            fromdate=hist_start_date,
            compression=30,
            ohlcv_limit=99999
        )

        # Add the feed
        cerebro.adddata(data)

    else:  # Backtesting with CSV file
        data = CustomDataset(
            name=COIN_TARGET,
            # dataname="dataset/bitstampUSD_1-min_data_2015-04-01_to_2018-04-01 trunc.csv",
            # dataname="dataset/bitmex-XBTUSD-1h.csv",
            # dataname="dataset/BTCUSDT-1h.csv",
            dataname="dataset/binance_nov_18_mar_19_btc.csv",
            timeframe=bt.TimeFrame.Minutes,
            fromdate=dt.datetime(2018, 3, 29),
            todate=dt.datetime(2019, 6, 26),
            # todate=dt.date.today(),
            nullvalue=0.0
        )

        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60)

        broker = cerebro.getbroker()
        broker.setcommission(commission=0.001, name=COIN_TARGET)  # Simulating exchange fee
        broker.setcash(100000.0)
        cerebro.addsizer(FullMoney)

    # Analyzers to evaluate trades and strategies
    # SQN = Average( profit / risk ) / StdDev( profit / risk ) x SquareRoot( number of trades )
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # Include Strategy
    cerebro.addstrategy(L1)

    # Starting backtrader bot
    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)
    result = cerebro.run()

    # Print analyzers - results
    final_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % final_value)
    print('Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100))
    print_trade_analysis(result[0].analyzers.ta.get_analysis())
    print_sqn(result[0].analyzers.sqn.get_analysis())

    if DEBUG:
        b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
        # cerebro.plot(b)
        # cerebro.plot()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("finished.")
        time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        send_telegram_message("Bot finished by user at %s" % time)
    except Exception as err:
        send_telegram_message("Bot finished with error: %s" % err)
        print("Finished with error: ", err)
        raise
