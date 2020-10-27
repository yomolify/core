from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
import backtrader as bt
from strategies.base import StrategyBase


class Momentum(bt.Indicator):
    lines = ('trend',)
    params = (('period', 90),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        returns = np.log(self.data.get(size=self.p.period))
        x = np.arange(len(returns))
        slope, _, rvalue, _, _ = linregress(x, returns)
        annualized = (1 + slope) ** 252
        self.lines.trend[0] = annualized * (rvalue ** 2)


class EquityMomentum(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),)

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.inds = {}
        self.spy = self.datas[0]
        self.stocks = self.datas[1:]
        self.orders = dict()

        self.spy_sma200 = bt.indicators.SimpleMovingAverage(self.spy.close,
                                                            period=200)
        for d in self.stocks:
            self.inds[d] = {}
            self.inds[d]["momentum"] = Momentum(d.close,
                                                period=90)
            self.inds[d]["sma100"] = bt.indicators.SimpleMovingAverage(d.close,
                                                                       period=100)
            self.inds[d]["atr20"] = bt.indicators.ATR(d,
                                                      period=20)

    def prenext(self):
        # call next() even when data is not available for all tickers
        self.next()

    def next(self):
        if self.i % 5 == 0:
            self.rebalance_portfolio()
        if self.i % 10 == 0:
            self.rebalance_positions()
        self.i += 1

    def rebalance_portfolio(self):
        # only look at data that we can have indicators for
        self.rankings = list(filter(lambda d: len(d) > 100, self.stocks))
        self.rankings.sort(key=lambda d: self.inds[d]["momentum"][0])
        num_stocks = len(self.rankings)

        # sell stocks based on criteria
        for i, d in enumerate(self.rankings):
            if self.getposition(self.data).size:
                if i > num_stocks * 0.2 or d < self.inds[d]["sma100"]:
                    self.close(d)

        if self.spy < self.spy_sma200:
            return

        # buy stocks with remaining cash
        for i, d in enumerate(self.rankings[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            if not self.getposition(self.data).size:
                size = value * 0.001 / self.inds[d]["atr20"]
                self.buy(d, size=size)

    def rebalance_positions(self):
        num_stocks = len(self.rankings)

        if self.spy < self.spy_sma200:
            return

        # rebalance all stocks
        for i, d in enumerate(self.rankings[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            size = value * 0.001 / self.inds[d]["atr20"]
            self.order_target_size(d, size)
#
# cerebro = bt.Cerebro(stdstats=False)
# cerebro.broker.set_coc(True)
#
# df = pd.read_csv(f"{historical_data}/binance-BTCUSDT-1d.csv",
#                      parse_dates=True,
#                      index_col=0)
#
# spy = bt.feeds.PandasData(dataname=df, plot=False)
# # spy = bt.feeds.YahooFinanceData(dataname='HODL.SW',
# #                                  fromdate=datetime(2018,11,1),
# #                                  todate=datetime(2020,10,21),
# #                                  plot=False)
# cerebro.adddata(spy)  # add S&P 500 Index
#
# for ticker in tickers:
#     # df = pd.read_csv(f"survivorship-free/{ticker}.csv",
#     df = pd.read_csv(f"{historical_data}/binance-{ticker}-1d.csv",
#                      parse_dates=True,
#                      index_col=0)
#     if len(df) > 100: # data must be long enough to compute 100 day SMA
#         cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False))
#
# cerebro.addobserver(bt.observers.Value)
# cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
# cerebro.addanalyzer(bt.analyzers.Returns)
# cerebro.addanalyzer(bt.analyzers.DrawDown)
# cerebro.addstrategy(Strategy)
# results = cerebro.run()
#
# cerebro.plot(iplot=False)[0][0]
# # print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
# print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
# print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
