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


datas = [bt.feeds.GenericCSVData(
            fromdate=start,
            todate=end,
            dataname=f"{historical_data}/binance-{ticker}-1h.csv",
            dtformat=lambda x: format_dt_hourly(x),
            # dtformat=lambda x: format_dt_daily(x),
            openinterest=-1,
            nullvalue=0.0,
            plot=False
        ) for ticker in tickers]


def backtest(datas, strategy, plot=None, **kwargs):
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.set_coc(True)
    cerebro.broker.setcash(1_000_000)
    for data in datas:
        cerebro.adddata(data)
    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addstrategy(strategy, **kwargs)
    results = cerebro.run()
    if plot:
        cerebro.plot(iplot=False)[0][0]
    return (results[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
            results[0].analyzers.returns.get_analysis()['rnorm100'],
            results[0].analyzers.sharperatio.get_analysis()['sharperatio'])






def min_n(array, n):
    return np.argpartition(array, n)[:n]


def max_n(array, n):
    return np.argpartition(array, -n)[-n:]


class CrossSectionalMR(bt.Strategy):
    params = (
        ('n', 10),
    )

    def __init__(self):
        self.inds = {}
        for d in self.datas:
            self.inds[d] = {}
            self.inds[d]["pct"] = bt.indicators.PercentChange(d.close, period=5)
            self.inds[d]["std"] = bt.indicators.StandardDeviation(d.close, period=5)

    def prenext(self):
        self.next()

    def next(self):
        available = list(filter(lambda d: len(d) > 5, self.datas))  # only look at data that existed last week
        rets = np.zeros(len(available))
        stds = np.zeros(len(available))
        for i, d in enumerate(available):
            rets[i] = self.inds[d]['pct'][0]
            stds[i] = self.inds[d]['std'][0]

        market_ret = np.mean(rets)
        weights = -(rets - market_ret)
        max_weights_index = max_n(np.abs(weights), self.params.n)
        low_volality_index = min_n(stds, self.params.n)
        selected_weights_index = np.intersect1d(max_weights_index,
                                                low_volality_index)
        if not len(selected_weights_index):
            # no good trades today
            return

        selected_weights = weights[selected_weights_index]
        weights = weights / np.sum(np.abs(selected_weights))
        for i, d in enumerate(available):
            if i in selected_weights_index:
                self.order_target_percent(d, target=weights[i])
            else:
                self.order_target_percent(d, 0)


dd, cagr, sharpe = backtest(datas, CrossSectionalMR, plot=True, n=10)
print(f"Max Drawdown: {dd:.2f}%\nAPR: {cagr:.2f}%\nSharpe: {sharpe:.3f}")
#
#
# cerebro.broker.setcash(1000000)
# cerebro.addobserver(bt.observers.Value)
# cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
# cerebro.addanalyzer(bt.analyzers.Returns)
# cerebro.addanalyzer(bt.analyzers.DrawDown)
# cerebro.addstrategy(CrossSectionalMR)
# results = cerebro.run()
#
# # print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
# print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
# print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
# cerebro.plot()[0][0]

# Norm. Annual Return: 6220611.57%
# Max Drawdown: 22.10%
