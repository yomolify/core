import collections
import math

from bokeh.models import HoverTool

from strategies.base import StrategyBase

import backtrader as bt
from backtrader.indicators import MovingAverageSimple
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT

# from indicators.Momentum import Momentum
from indicators.SuperTrend import SuperTrend

import backtrader as bt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.themes import built_in_themes
from bokeh.io import curdoc
from bokeh.palettes import all_palettes
import itertools





# from scipy import stats

class Momo(StrategyBase):
    params = dict(
        exectype=bt.Order.Market,
        selcperc=0.50,  # percentage of stocks to select from the universe
        rperiod=5,  # period for the returns calculation, default 1 period
        vperiod=36,  # lookback period for volatility - default 36 periods
        mperiod=5,  # lookback period for strategy - default 12 periods
        reserve=0.05,  # 5% reserve capital
        order_target_percent=10
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.mean_returns = []
        self.strategy = "Momo"
        length = len(self.datas)
        self.p.order_target_percent = 75/length
        if self.p.order_target_percent > 10:
            self.p.order_target_percent = 10
        middle_index = length // 2
        # self.datas = self.datas[:middle_index]
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
        self.placed_orders = None
        self.buy_price_close = None
        self.sell_price_close = None
        self.executed_size = None
        self.entry_bar_height = None
        self.to_place_orders = []
        self.first_bar_after_entry = dict()
        # self.inds = collections.defaultdict(dict)
        self.inds = {}
        self.unique = 0
        self.pos = {}
        self.flags = {}
        self.orders = dict()
        self.stop_order = dict()
        self.entry_order = dict()
        self.returns = dict()

        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            # ticker = ticker[3:]
            self.inds[ticker] = {}
            self.pos[ticker] = {}
            self.returns[ticker] = []

        for d in self.datas:
            ticker = d._name
            self.pos[ticker]["sl_price"] = None
            self.pos[ticker]["new_sl_price"] = None
            self.pos[ticker]["profit_arr"] = []
            self.pos[ticker]["profit_roc"] = []
            self.inds[ticker]["atr"] = bt.indicators.ATR(d, plot=False, subplot=False)
            self.inds[ticker]["volatility"] = 1 / ((self.inds[ticker]["atr"] / d.high) * 100)
            self.inds[ticker]["volsma_slow"] = bt.indicators.EMA(d.close, period=50, plot=False, subplot=False)
            self.inds[ticker]["volsma_fast"] = bt.indicators.EMA(d.close, period=20, plot=False, subplot=False)
            self.inds[ticker]["hh"] = bt.indicators.Highest(d.high, period=50, plot=False, subplot=False)
            self.inds[ticker]["hh_fast"] = bt.indicators.Highest(d.high, period=10, plot=False, subplot=False)
            self.inds[ticker]["hh_fastest"] = bt.indicators.Highest(d.high, period=2, plot=False, subplot=False)
            self.inds[ticker]["ll"] = bt.indicators.Lowest(d.low, period=50, plot=False, subplot=False)
            self.inds[ticker]["ll_fast"] = bt.indicators.Lowest(d.low, period=10, plot=False, subplot=False)
            self.inds[ticker]["ll_fastest"] = bt.indicators.Lowest(d.low, period=2, plot=False, subplot=False)
            self.inds[ticker]["sma5"] = bt.indicators.EMA(d.close, period=5, plot=False, subplot=False)
            self.inds[ticker]["sma20"] = bt.indicators.EMA(d.close, period=20, plot=False, subplot=False)
            self.inds[ticker]["sma50"] = bt.indicators.EMA(d.close, period=50, plot=False, subplot=False)
            self.inds[ticker]["sma100"] = bt.indicators.EMA(d.close, period=100, plot=False, subplot=False)
            self.inds[ticker]["sma240"] = bt.indicators.SMA(d.close, period=240, plot=False, subplot=False)
            self.inds[ticker]["pct_change"] = bt.indicators.PctChange(d.close, period=200, plot=True, subplot=True)
            self.inds[ticker]["std"] = bt.indicators.StandardDeviation(d.close, period=30, plot=False)
            self.inds[ticker]["pct_change_vol_sma"] = bt.indicators.PctChange(self.inds[ticker]["volsma_fast"], plot=False, subplot=False)

    def next(self):
        self.calc_mean_returns()
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            self.datas.sort(reverse=True, key=lambda d: abs(self.inds[d._name]["pct_change"][0]))
            for d in self.datas:
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                # if current_position > 0:
                #     if self.stop_order:
                #         self.cancel(self.stop_order)
                #     self.stop_order = self.close(d, exectype=bt.Order.StopTrail, trailamount=self.inds[ticker]["ll"][0])
                # elif current_position < 0:
                #     if self.inds[ticker]["roc_std_sma10"][-1] > self.inds[ticker]["roc_std_sma20"][-1] and self.inds[ticker]["roc_std_sma10"][0] < self.inds[ticker]["roc_std_sma20"][0]:
                #         self.order_target_percent(d, target=0)
                #     if self.stop_order:
                #         self.cancel(self.stop_order)
                #     self.stop_order = self.close(d, exectype=bt.Order.StopTrail, trailamount=self.inds[ticker]["hh"][-1])

                self.pos[ticker]["size"] = self.get_position(d=d, attribute='size')
                self.pos[ticker]["price"] = self.get_position(d=d, attribute='price')
                if current_position > 0:
                    # StopWin
                    self.pos[ticker]["profit"] = d.close[0] - self.pos[ticker]["price"]
                    self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker][
                        "price"]) * 100
                    self.pos[ticker]["profit_arr"].append(self.pos[ticker]["profit_percentage"])
                    # if len(self.pos[ticker]["profit_arr"]) > 1 and abs(self.pos[ticker]["profit_arr"][-2]) > 0:
                    #     self.pos[ticker]["profit_roc"].append(((self.pos[ticker]["profit_arr"][-1] - self.pos[ticker]["profit_arr"][-2])/self.pos[ticker]["profit_arr"][-2])*100)
                    #     self.log(self.pos[ticker]["profit_roc"])
                    if self.pos[ticker]["profit_percentage"] > 95:
                        # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                        self.pos[ticker]["new_sl_price"] = 1.8 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 85:
                        # self.log(f'{ticker} Long profit > 85%')
                        self.pos[ticker]["new_sl_price"] = 1.7 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 75:
                        # self.log(f'{ticker} Long profit > 75%')
                        self.pos[ticker]["new_sl_price"] = 1.6 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 65:
                        # self.log(f'{ticker} Long profit > 65%')
                        self.pos[ticker]["new_sl_price"] = 1.5 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 55:
                        # self.log(f'{ticker} Long profit > 55%')
                        self.pos[ticker]["new_sl_price"] = 1.4 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 45:
                        # self.log(f'{ticker} Long profit > 45%')
                        self.pos[ticker]["new_sl_price"] = 1.3 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 35:
                        # self.log(f'{ticker} Long profit > 35%')
                        self.pos[ticker]["new_sl_price"] = 1.2 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 25:
                        # self.log(f'{ticker} Long profit > 25%')
                        self.pos[ticker]["new_sl_price"] = 1.1 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 15:
                        # self.log(f'{ticker} Long profit > 15%')
                        self.pos[ticker]["new_sl_price"] = 1.05 * self.pos[ticker]["price"]
                        # self.pos[ticker]["new_sl_price"] = (1 + ((self.pos[ticker]["profit_percentage"]-4)*0.01)) * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > 5:
                        # self.log(f'{ticker} Long profit > 5')
                        # self.pos[ticker]["new_sl_price"] = (1 + ((self.pos[ticker]["profit_percentage"]-5)*0.01)) * self.pos[ticker]["price"]
                        self.pos[ticker]["new_sl_price"] = 1 * self.pos[ticker]["price"]
                    # if self.pos[ticker]["profit_percentage"] < 0 and math.trunc(self.pos[ticker]["profit_percentage"]) % 1 == 0 and not self.flags[ticker][f"add_position_{math.trunc(self.pos[ticker]['profit_percentage']) - 1}"]:
                    #     self.buy(d, size=(self.pos[ticker]["profit_percentage"] / 100) * current_position)
                    #     self.flags[ticker][f"add_position_{math.trunc(self.pos[ticker]['profit_percentage'])}"] = True
                    #     self.log(f'{ticker} adding to position at {self.pos[ticker]["profit_percentage"]}')

                    # if self.pos[ticker]["profit_percentage"] - self.pos[ticker]["profit_percentage_-1"] > 1.1:
                    #     self.pos[ticker]["new_sl_price"] = (1 + ((self.pos[ticker]["profit_percentage"]-1) * 0.01)) * self.pos[ticker]["price"]

                    # if (self.pos[ticker]["profit_percentage"] - self.pos[ticker]["profit_percentage_-1"]) > 0.2*self.pos[ticker]["profit_percentage_-1"]:
                    #     self.pos[ticker]["new_sl_price"] = (1 + ((self.pos[ticker]["profit_percentage"]-1) * 0.01)) * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] < 5:
                    #     self.buy(d, size=abs(self.pos[ticker]["size"])/2)
                    # if self.pos[ticker]["profit_percentage"] < 5:
                        # self.log(f'{ticker} Long profit > 5%, updating stop win to 0%')
                        # self.close(d)
                    # if self.pos[ticker]["profit_percentage"] > 25:
                    #     self.pos[ticker]["new_sl_price"] = self.inds[ticker]["ll_fastest"][0]
                    # elif self.pos[ticker]["profit_percentage"] > 15:
                    #     self.pos[ticker]["new_sl_price"] = self.inds[ticker]["ll_fast"][0]
                    # elif self.pos[ticker]["profit_percentage"] > 5:
                    #     self.pos[ticker]["new_sl_price"] = self.inds[ticker]["ll"][0]
                    if self.pos[ticker]["new_sl_price"] and self.pos[ticker]["sl_price"] and self.pos[ticker]["new_sl_price"] > self.pos[ticker]["sl_price"]:
                        self.log(
                            f'{ticker} LONG Update stop from {self.pos[ticker]["sl_price"]} to {self.pos[ticker]["new_sl_price"]}')
                        self.pos[ticker]["sl_price"] = self.pos[ticker]["new_sl_price"]
                        if (ticker in self.stop_order) and (self.stop_order[ticker] is not None):
                            self.cancel(self.stop_order[ticker])
                            self.stop_order[ticker] = None
                        self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)

                # if current_position < 0:
                #     # StopWin
                #     self.pos[ticker]["profit"] = self.pos[ticker]["price"] - d.close[0]
                #     self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker][
                #         "price"]) * 100
                #     # self.pos[ticker]["profit_arr"].append(self.pos[ticker]["profit_percentage"])
                #     # if self.pos[ticker]["profit_percentage"] > 95:
                #     #     # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.555 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 85:
                #     #     # self.log(f'{ticker} Long profit > 85%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.588 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 75:
                #     #     # self.log(f'{ticker} Long profit > 75%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.625 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 65:
                #     #     # self.log(f'{ticker} Long profit > 65%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.67 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 55:
                #     #     # self.log(f'{ticker} Long profit > 55%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.71 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 45:
                #     #     # self.log(f'{ticker} Long profit > 45%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.77 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 35:
                #     #     # self.log(f'{ticker} Long profit > 35%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.83 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 25:
                #     #     # self.log(f'{ticker} Long profit > 25%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.9 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 15:
                #     #     # self.log(f'{ticker} Long profit > 15%')
                #     #     self.pos[ticker]["new_sl_price"] = 0.95 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] > 5:
                #     #     # self.log(f'{ticker} Long profit > 5')
                #     #     self.pos[ticker]["new_sl_price"] = 1 * self.pos[ticker]["price"]
                #     if self.pos[ticker]["profit_percentage"] > self.inds[ticker]["volatility"][0]*25:
                #         self.log(f'{ticker} Short profit > 25')
                #         self.pos[ticker]["new_sl_price"] = self.inds[ticker]["hh_fastest"][0]
                #     elif self.pos[ticker]["profit_percentage"] > self.inds[ticker]["volatility"][0]*15:
                #         self.log(f'{ticker} Short profit > 15')
                #         self.pos[ticker]["new_sl_price"] = self.inds[ticker]["hh_fast"][0]
                #         # self.pos[ticker]["new_sl_price"] = (1 + ((self.pos[ticker]["profit_percentage"]+4)*0.01)) * 1 * self.pos[ticker]["price"]
                #     elif self.pos[ticker]["profit_percentage"] > self.inds[ticker]["volatility"][0]*5:
                #         self.log(f'{ticker} Short profit > 5')
                #         self.pos[ticker]["new_sl_price"] = self.inds[ticker]["hh"][0]
                #         # self.pos[ticker]["new_sl_price"] = (1 + ((self.pos[ticker]["profit_percentage"]+5)*0.01)) * 1 * self.pos[ticker]["price"]
                #     # elif self.pos[ticker]["profit_percentage"] < 5:
                #     #     self.sell(d, size=abs(self.pos[ticker]["size"])/2)
                #     if self.pos[ticker]["new_sl_price"] and self.pos[ticker]["sl_price"] and self.pos[ticker]["new_sl_price"] < self.pos[ticker]["sl_price"]:
                #         self.log(
                #             f'{ticker} SHORT Update stop from {self.pos[ticker]["sl_price"]} to {self.pos[ticker]["new_sl_price"]}')
                #         self.pos[ticker]["sl_price"] = self.pos[ticker]["new_sl_price"]
                #         if (ticker in self.stop_order) and (self.stop_order[ticker] is not None):
                #             self.cancel(self.stop_order[ticker])
                #             self.stop_order[ticker] = None
                #         self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)

                # if current_position > 0:
                #     if self.inds[ticker]["sma50"][0] < self.inds[ticker]["sma100"][0]:
                #         self.close(d)
                # elif current_position < 0:
                #     if self.inds[ticker]["sma50"][0] > self.inds[ticker]["sma100"][0]:
                #         self.close(d)

                # TO OPEN POSITIONS ONLY IN TOP RANKED COINS, UNCOMMENT BLOCK BELOW
                # for d in self.datas[0:7]:
                #     ticker = d._name
                #     current_position = self.get_position(d=d, attribute='size')
                #     self.log(f'{ticker} {self.pos[ticker]["profit_arr"]}')
                if current_position > 0:
                    if self.returns[ticker][-1] < self.mean_returns[-1]:
                        d.close()

                if self.mean_returns[-1] > 0:
                    self.log(f'{ticker}: {self.returns[ticker][-1]}, Mean: {self.mean_returns[-1]}')
                    if self.returns[ticker][-1] > 1.01*self.mean_returns[-1]:
                        # self.log(f'{ticker}: {self.returns[ticker][-1]} > {self.mean_returns[-1]}')
                        if current_position == 0:
                            if (ticker in self.stop_order) and (self.stop_order[ticker] is not None):
                                self.cancel(self.stop_order[ticker])
                                self.stop_order[ticker] = None
                            self.pos[ticker]["price"] = None
                            self.entry_order[ticker] = self.add_order(d, target=(self.p.order_target_percent / 100))
                            # self.entry_order[ticker] = self.add_order(d, target=((self.p.order_target_percent / 100) * self.inds[ticker]["volatility"][0]))
                            # self.entry_order[ticker] = self.order_target_percent(d, target=((self.p.order_target_percent / 100) * self.inds[ticker]["volatility"][0])*0.67, price=d.close[0]-self.inds[ticker]["atr"][0]/3, exectype=bt.Order.Limit)
                            self.pos[ticker]["sl_price"] = 0.5 * d.close[0]
                            self.pos[ticker]["new_sl_price"] = None
                            # elif self.inds[ticker]["sma20"][0] < self.inds[ticker]["sma50"][0] < self.inds[ticker]["sma100"][0] < self.inds[ticker]["sma240"][0]:  # look for longs
                            #     self.entry_order[ticker] = self.add_order(d, target=-((self.p.order_target_percent / 100) * self.inds[ticker]["volatility"][0]))
                            # self.entry_order[ticker] = self.order_target_percent(d, target=-((self.p.order_target_percent / 100) * self.inds[ticker]["volatility"][0])/2, price=d.close[0]+self.inds[ticker]["atr"][0]/2)
                            # self.pos[ticker]["sl_price"] = 2 * d.close[0]
                            # self.pos[ticker]["new_sl_price"] = None
                else:
                    self.close(d)

                if self.to_place_orders is not None and len(self.to_place_orders) > 0:
                    print(self.to_place_orders)
                    order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                    for order_chunk in order_chunks:
                        self.placed_orders = self.place_batch_order(order_chunk)

                for i, d in enumerate(self.datas):
                    ticker = d._name
                    if self.placed_orders is not None:
                        for placed_order in self.placed_orders:
                            if placed_order.ccxt_order["symbol"] == ticker:
                                # Only remember the most recently placed order for a ticker, TODO: improve soon
                                self.orders[ticker] = placed_order


    def calc_mean_returns(self):
        available = list(filter(lambda d: len(d) > 10, self.datas))  # only look at data that existed last week
        rets = np.zeros(len(available))
        for i, d in enumerate(available):
            rets[i] = self.inds[d._name]["pct_change"][0]
            self.returns[d._name].append(self.inds[d._name]["pct_change"][0])
        self.mean_returns.append(np.mean(rets))

    # def stop(self):
    #     colors = itertools.cycle(all_palettes['Turbo'][10])
    #     HoverTool(
    #         tooltips=[
    #             ("Date", "$x"),
    #             ("% return", "$y"),
    #         ],
    #
    #         formatters={
    #             '@date': 'datetime',  # use 'datetime' formatter for '@date' field
    #             '@{adj close}': 'printf',  # use 'printf' formatter for '@{adj close}' field
    #             # use default 'numeral' formatter for other fields
    #         },
    #
    #         # display a tooltip whenever the cursor is vertically in line with a glyph
    #         mode='vline'
    #     )
    #     tooltips = [
    #        ("Date", "$x"),
    #        ("% return", "$y"),
    #     ]
    #     p = figure(title="caliber", x_axis_label='', y_axis_label='Mean Returns', plot_width=1800, plot_height=1000, tools='hover, crosshair', tooltips=tooltips)
    #     curdoc().theme = 'dark_minimal'
    #     x = range(1, len(self.mean_returns) + 1, 1)
    #     p.line(x, self.mean_returns, color=next(colors), legend_label="Mean")
    #     for i, ticker in enumerate(self.returns):
    #         p.line(x, self.returns[ticker], color=next(colors), legend_label=f"{ticker}")
    #     p.legend.location = "top_right"
    #
    #     show(p)
