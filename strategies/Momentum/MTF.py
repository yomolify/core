import collections
from strategies.base import StrategyBase

import backtrader as bt
from backtrader.indicators import MovingAverageSimple

# from indicators.Momentum import Momentum
from indicators.SuperTrend import SuperTrend

import backtrader as bt
import numpy as np
import pandas as pd
# from scipy import stats

class MTF(StrategyBase):
    params = dict(
        exectype=bt.Order.Market,
        selcperc=0.50,  # percentage of stocks to select from the universe
        rperiod=5,  # period for the returns calculation, default 1 period
        vperiod=36,  # lookback period for volatility - default 36 periods
        mperiod=5,  # lookback period for strategy - default 12 periods
        reserve=0.05  # 5% reserve capital
    )

    def __init__(self):
        self.dataclose = self.datas[0].close

        length = len(self.datas)
        middle_index = length // 2
        self.datas_5m = self.datas[:middle_index]
        self.datas_1h = self.datas[middle_index:]

        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.open_orders = {}
        self.window = 0
        self.started = False

        self.sl_price = None
        self.new_sl_price = None
        self.tp_price = None
        self.profit_percentage = None
        self.long_order = None
        self.long_stop_order = None
        self.short_order = None
        self.short_stop_order = None
        self.stop_order = None
        self.slow_sma_stop_win = False
        self.last_operation = "SELL"
        self.status = "DISCONNECTED"
        self.buy_price_close = None
        self.sell_price_close = None
        self.executed_size = None
        self.strategy = None
        self.entry_bar_height = None
        self.to_place_orders = []
        self.first_bar_after_entry = dict()
        # self.inds = collections.defaultdict(dict)
        self.inds = {}

        for d in self.datas:
            ticker = d._name
            ticker = ticker[3:]
            self.inds[ticker] = {}
        for d in self.datas_5m:
            ticker = d._name
            ticker = ticker[3:]
            self.inds[ticker]["sma20_5m"] = bt.indicators.SMA(d.close, period=20, plot=True, subplot=False)
            self.inds[ticker]["sma50_5m"] = bt.indicators.SMA(d.close, period=50, plot=True, subplot=False)
            self.inds[ticker]["sma100_5m"] = bt.indicators.SMA(d.close, period=100, plot=True, subplot=False)
            self.inds[ticker]["roc"] = bt.indicators.ROC(d.close, period=10, plot=True, subplot=True)
            self.inds[ticker]["roc_std"] = bt.indicators.StdDev(self.inds[ticker]["roc"], period=10, plot=True, subplot=True)
            self.inds[ticker]["roc_std_sma10"] = bt.indicators.SMA(self.inds[ticker]["roc_std"], period=10, plot=True, subplot=True)
            self.inds[ticker]["roc_std_sma50"] = bt.indicators.SMA(self.inds[ticker]["roc_std"], period=50, plot=True, subplot=True)
            self.inds[ticker]["st_5m"] = SuperTrend(d, plot=True)
        for d in self.datas_1h:
            ticker = d._name
            ticker = ticker[3:]
            self.inds[ticker]["sma5_1h"] = bt.indicators.SMA(d.close, period=5, plot=True, subplot=False)
            self.inds[ticker]["sma20_1h"] = bt.indicators.EMA(d.close, period=20, plot=True, subplot=False)
            self.inds[ticker]["sma50_1h"] = bt.indicators.SMA(d.close, period=50, plot=True, subplot=False)
            self.inds[ticker]["st_1h"] = SuperTrend(d, plot=True)


        # calculate 1st the amount of stocks that will be selected
        # self.selnum = int(len(self.datas) * self.p.selcperc)

        # allocation per stock
        # reserve kept to make sure orders are not rejected due to
        # margin. Prices are calculated when known (close), but orders can only
        # be executed next day (opening price). Price can gap upwards
        # self.perctarget = (1.0 - self.p.reserve) % self.selnum

        # returns, volatilities and strategy
        # rs = [bt.ind.PctChange(d, period=self.p.rperiod) for d in self.datas]
        # vs = [bt.ind.StdDev(ret, period=self.p.vperiod) for ret in rs]
        # ms = [bt.ind.ROC(d, period=self.p.mperiod) for d in self.datas]

        # simple rank formula: (strategy * net payout) / volatility
        # the highest ranked: low vol, large strategy, large payout
        # self.ranks = {d: 5 * m / v for d, v, m in zip(self.datas_5m, vs, ms)}

    def next(self):
        for d in self.datas_5m:
            ticker = d._name
            ticker = ticker[3:]
            # if not self.broker.getposition(d):
            if d.close[0] > self.inds[ticker]["sma5_1h"] > self.inds[ticker]["sma20_1h"] and d.close[0] > self.inds[ticker]["sma20_5m"]:
                self.order_target_percent(d, target=0.5)
            elif d.close[0] < self.inds[ticker]["sma5_1h"] < self.inds[ticker]["sma20_1h"] and d.close[0] < self.inds[ticker]["sma20_5m"]:
                self.order_target_percent(d, target=-0.5)
            # current_position = self.get_position(d=d, attribute='size')
            # if current_position > 0:
            #     if d.close[0] < self.inds[ticker]["sma20_1h"]:
            #         self.order_target_percent(d, target=0)
            # elif current_position < 0:
            #     if d.close[0] > self.inds[ticker]["sma20_1h"]:
            #         self.order_target_percent(d, target=0)

