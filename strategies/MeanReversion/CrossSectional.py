import pandas as pd
import backtrader as bt
import numpy as np
from datetime import datetime
import fnmatch
import os

tickers = []
historical_data = '../../code/fetch-historical-data'
# Fetch all USDT tickers and append to tickers list
# for file in os.listdir(historical_data):
#     if fnmatch.fnmatch(file, '*USDT-1h*.csv'):
#         # Remove -1m.csv
#         file = file[:-7]
#         # Remove binance-
#         file = file[8:]
#         # Remove USDT
#         file = file[:-4]
#         tickers.append(file)
#
# print(tickers)

tickers = ['BTCUSDT', 'ETHUSDT', 'BCHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT',
           'ETCUSDT', 'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT',
           'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT',
           'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT', 'ALGOUSDT', 'ZILUSDT',
           'KNCUSDT', 'ZRXUSDT', 'COMPUSDT', 'OMGUSDT', 'DOGEUSDT', 'SXPUSDT', 'KAVAUSDT',
           'BANDUSDT', 'RLCUSDT', 'WAVESUSDT', 'MKRUSDT', 'SNXUSDT', 'DOTUSDT', 'YFIUSDT',
           'BALUSDT', 'CRVUSDT', 'TRBUSDT', 'YFIIUSDT', 'RUNEUSDT', 'SUSHIUSDT', 'SRMUSDT',
           'BZRXUSDT', 'EGLDUSDT', 'SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'BLZUSDT', 'UNIUSDT',
           'AVAXUSDT', 'FTMUSDT', 'ENJUSDT', 'TOMOUSDT', 'RENUSDT',
           'KSMUSDT', 'RSRUSDT', 'LRCUSDT']

# Very new
not_considered = ['HNTUSDT', 'FLMUSDT', 'NEARUSDT', 'AAVEUSDT', 'FILUSDT']

class CrossSectionalMR(bt.Strategy):
    def prenext(self):
        self.next()

    def next(self):
        # only look at data that existed yesterday
        available = list(filter(lambda d: len(d), self.datas))

        rets = np.zeros(len(available))
        for i, d in enumerate(available):
            # if d.close[-1] == 0.0:
            #     continue
            # calculate individual daily returns
            rets[i] = (d.close[0] - d.close[-1]) / d.close[-1]

        # calculate weights using formula
        market_ret = np.mean(rets)
        weights = -(rets - market_ret)
        print(weights)
        print(np.abs(weights))
        print(np.sum(np.abs(weights)))
        weights = weights / np.sum(np.abs(weights))

        for i, d in enumerate(available):
            self.order_target_percent(d, target=weights[i])


cerebro = bt.Cerebro(stdstats=False)
cerebro.broker.set_coc(True)

end = datetime.now()
start = datetime(end.year - 1, end.month, end.day)
end = datetime(end.year, end.month, end.day - 1)


def format_dt_daily(dt):
    if len(dt) > 10:
        dt = dt[:-9]
    return datetime.strptime(dt, '%Y-%m-%d')


def format_dt_hourly(dt):
    if len(dt) > 19:
        dt = dt[:-4]
    return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')


for ticker in tickers:
    data = bt.feeds.GenericCSVData(
        fromdate=start,
        todate=end,
        dataname=f"{historical_data}/binance-{ticker}-1h.csv",
        # dtformat='%Y-%m-%d',
        # dtformat=lambda x: format_dt_daily(x),
        dtformat=lambda x: format_dt_hourly(x),
        # dtformat='%Y-%m-%d %H:%M:%S',
        openinterest=-1,
        nullvalue=0.0,
        plot=False
    )
    cerebro.adddata(data)

cerebro.broker.setcash(1000000)
cerebro.addobserver(bt.observers.Value)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
cerebro.addanalyzer(bt.analyzers.Returns)
cerebro.addanalyzer(bt.analyzers.DrawDown)
cerebro.addstrategy(CrossSectionalMR)
results = cerebro.run()

# print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
# cerebro.plot()[0][0]

# Norm. Annual Return: 6220611.57%
# Max Drawdown: 22.10%
