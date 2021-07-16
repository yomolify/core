import collections
from strategies.base import StrategyBase

import backtrader as bt
from backtrader.indicators import MovingAverageSimple
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT

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
        reserve=0.05,  # 5% reserve capital
        order_target_percent=2
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.strategy = "MTF"

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
        self.entry_bar_height = None
        self.to_place_orders = []
        self.first_bar_after_entry = dict()
        # self.inds = collections.defaultdict(dict)
        self.inds = {}
        self.unique = 0

        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            ticker = ticker[3:]
            self.inds[ticker] = {}
        for d in self.datas_5m:
            ticker = d._name
            ticker = ticker[3:]
            self.inds[ticker]["rsi_5m"] = bt.indicators.RSI(d, plot=True, subplot=True)
            self.inds[ticker]["adx_5m"] = bt.indicators.ADX(d, plot=True, subplot=True)
            self.inds[ticker]["atr_5m"] = bt.indicators.ATR(d, plot=True, subplot=True)
            self.inds[ticker]["hh_5m"] = bt.indicators.Highest(d.high, plot=True, subplot=True)
            self.inds[ticker]["ll_5m"] = bt.indicators.Lowest(d.low, plot=True, subplot=True)
            self.inds[ticker]["sma20_5m"] = bt.indicators.EMA(d.close, period=20, plot=True, subplot=False)
            self.inds[ticker]["sma50_5m"] = bt.indicators.EMA(d.close, period=50, plot=True, subplot=False)
            self.inds[ticker]["sma100_5m"] = bt.indicators.EMA(d.close, period=100, plot=True, subplot=False)
            self.inds[ticker]["roc"] = bt.indicators.ROC(d.close, period=10, plot=True, subplot=True)
            self.inds[ticker]["roc_std"] = bt.indicators.StdDev(self.inds[ticker]["roc"], period=10, plot=True, subplot=True)
            self.inds[ticker]["roc_std_sma10"] = bt.indicators.EMA(self.inds[ticker]["roc_std"], period=10, plot=True, subplot=True)
            self.inds[ticker]["roc_std_sma20"] = bt.indicators.EMA(self.inds[ticker]["roc_std"], period=20, plot=True, subplot=True)
            self.inds[ticker]["roc_std_sma20"].plotinfo.plotmaster = self.inds[ticker]["roc_std_sma10"]
            self.inds[ticker]["roc_std_sma50"] = bt.indicators.EMA(self.inds[ticker]["roc_std"], period=50, plot=True, subplot=True)
            self.inds[ticker]["roc_std_sma50"].plotinfo.plotmaster = self.inds[ticker]["roc_std_sma10"]
            self.inds[ticker]["roc_std_sma200"] = bt.indicators.EMA(self.inds[ticker]["roc_std"], period=200, plot=True, subplot=True)
            self.inds[ticker]["roc_std_sma200"].plotinfo.plotmaster = self.inds[ticker]["roc_std_sma10"]

            self.inds[ticker]["st_5m"] = SuperTrend(d, plot=True)
        for d in self.datas_1h:
            ticker = d._name
            ticker = ticker[3:]
            # self.inds[ticker]["rsi_1h"] = bt.indicators.RSI(d, plot=True, subplot=True)
            # self.inds[ticker]["adx_1h"] = bt.indicators.ADX(d, plot=True, subplot=True)
            # self.inds[ticker]["hh_1h"] = bt.indicators.Highest(d.high, plot=True, subplot=True)
            # self.inds[ticker]["ll_1h"] = bt.indicators.Lowest(d.low, plot=True, subplot=True)
            # self.inds[ticker]["atr_1h"] = bt.indicators.ATR(d, plot=True, subplot=True)
            self.inds[ticker]["sma5_1h"] = bt.indicators.EMA(d.close, period=5, plot=True, subplot=False)
            self.inds[ticker]["sma20_1h"] = bt.indicators.EMA(d.close, period=20, plot=True, subplot=False)
            # self.inds[ticker]["sma50_1h"] = bt.indicators.EMA(d.close, period=50, plot=True, subplot=False)
            # self.inds[ticker]["st_1h"] = SuperTrend(d, plot=True)


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
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            self.datas_5m.sort(reverse=True, key=lambda d: (self.inds[d._name[3:]]["rsi_5m"][0] * self.inds[d._name[3:]]["adx_5m"][0]) * (self.inds[d._name[3:]]["roc"][0]))
            for d in self.datas_5m:
                ticker = d._name
                ticker = ticker[3:]
                current_position = self.get_position(d=d, attribute='size')
                # if current_position > 0:
                #     if self.stop_order:
                #         self.cancel(self.stop_order)
                    # self.stop_order = self.close(d, exectype=bt.Order.StopTrail, trailamount=self.inds[ticker]["ll_5m"][0])
                # elif current_position < 0:
                    # if self.inds[ticker]["roc_std_sma10"][-1] > self.inds[ticker]["roc_std_sma20"][-1] and self.inds[ticker]["roc_std_sma10"][0] < self.inds[ticker]["roc_std_sma20"][0]:
                    #     self.order_target_percent(d, target=0)
                    # if self.stop_order:
                    #     self.cancel(self.stop_order)
                    # self.stop_order = self.close(d, exectype=bt.Order.StopTrail, trailamount=self.inds[ticker]["hh_5m"][-1])


                # if self.stop_order:
                #     self.cancel(self.stop_order)
                if d.close[0] > self.inds[ticker]["sma5_1h"] > self.inds[ticker]["sma20_1h"] and d.close[0] > self.inds[ticker]["sma20_5m"]:
                    volatility = self.inds[ticker]["atr_5m"][0] / d.close[0]
                    volatility_factor = 1 / (volatility * 100)
                    self.add_order(d, target=((self.p.order_target_percent/100) * volatility_factor), type="market")
                    # self.order_target_percent(d, target=0.25)
                elif d.close[0] < self.inds[ticker]["sma5_1h"] < self.inds[ticker]["sma20_1h"] and d.close[0] < self.inds[ticker]["sma20_5m"]:
                    volatility = self.inds[ticker]["atr_5m"][0] / d.close[0]
                    volatility_factor = 1 / (volatility * 100)
                    self.add_order(d, target=-((self.p.order_target_percent / 100) * volatility_factor), type="market")

                if len(self.to_place_orders) > 0:
                    print(self.to_place_orders)
                    order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                    for order_chunk in order_chunks:
                        self.place_batch_order(order_chunk)
                # else:
                #     self.unique = self.unique + 1
                #     self.log('unique case')

                    # if self.unique > 10:
                    #     self.order_target_percent(d, target=0)
                    #     self.unique = 0
                # elif current_position < 0:
                #     if d.close[0] > self.inds[ticker]["sma20_1h"]:
                #         self.order_target_percent(d, target=0)

