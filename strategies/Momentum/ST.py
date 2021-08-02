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

class ST(StrategyBase):
    params = dict(
        exectype=bt.Order.Market,
        selcperc=0.50,  # percentage of stocks to select from the universe
        rperiod=5,  # period for the returns calculation, default 1 period
        vperiod=36,  # lookback period for volatility - default 36 periods
        mperiod=5,  # lookback period for strategy - default 12 periods
        reserve=0.05,  # 5% reserve capital
        order_target_percent=5
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.strategy = "ST"

        length = len(self.datas)
        middle_index = length // 2
        # self.datas_5m = self.datas[:middle_index]
        self.datas_5m = self.datas
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
        self.orders = dict()
        self.stop_order = dict()
        self.entry_order = dict()

        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            # ticker = ticker[3:]
            self.inds[ticker] = {}
            self.pos[ticker] = {}
        for d in self.datas_5m:
            ticker = d._name
            self.pos[ticker]["sl_price"] = None
            self.pos[ticker]["new_sl_price"] = None
            # self.pos[ticker]["price"] = None
            # ticker = ticker[3:]
            # self.inds[ticker]["rsi_5m"] = bt.indicators.RSI(d, plot=False, subplot=False)
            # self.inds[ticker]["adx_5m"] = bt.indicators.ADX(d, plot=True, subplot=True)
            self.inds[ticker]["atr_5m"] = bt.indicators.ATR(d, plot=False, subplot=False)
            self.inds[ticker]["volatility_5m"] = 1 / ((self.inds[ticker]["atr_5m"] / d.high) * 100)
            self.inds[ticker]["volsma_slow_5m"] = bt.indicators.EMA(d.close, period=50, plot=False, subplot=False)
            self.inds[ticker]["volsma_fast_5m"] = bt.indicators.EMA(d.close, period=20, plot=False, subplot=False)
            self.inds[ticker]["hh_5m"] = bt.indicators.Highest(d.high, period=50, plot=False, subplot=False)
            self.inds[ticker]["hh_fast_5m"] = bt.indicators.Highest(d.high, period=10, plot=False, subplot=False)
            self.inds[ticker]["hh_fastest_5m"] = bt.indicators.Highest(d.high, period=2, plot=False, subplot=False)
            self.inds[ticker]["ll_5m"] = bt.indicators.Lowest(d.low, period=50, plot=False, subplot=False)
            self.inds[ticker]["ll_fast_5m"] = bt.indicators.Lowest(d.low, period=10, plot=False, subplot=False)
            self.inds[ticker]["ll_fastest_5m"] = bt.indicators.Lowest(d.low, period=2, plot=False, subplot=False)
            self.inds[ticker]["sma5_5m"] = bt.indicators.EMA(d.close, period=5, plot=False, subplot=False)
            self.inds[ticker]["sma20_5m"] = bt.indicators.EMA(d.close, period=20, plot=True, subplot=False)
            self.inds[ticker]["sma50_5m"] = bt.indicators.EMA(d.close, period=50, plot=True, subplot=False)
            # self.inds[ticker]["sma60_5m"] = bt.indicators.EMA(d.close, period=60, plot=True, subplot=False)
            self.inds[ticker]["sma100_5m"] = bt.indicators.EMA(d.close, period=100, plot=True, subplot=False)
            self.inds[ticker]["sma240_5m"] = bt.indicators.SMA(d.close, period=240, plot=True, subplot=False)
            # self.inds[ticker]["roc"] = bt.indicators.ROC(d.close, period=10, plot=False, subplot=False)
            self.inds[ticker]["pct_change"] = bt.indicators.PctChange(d.close, plot=False, subplot=False)
            # self.inds[ticker]["roc_std"] = bt.indicators.StdDev(self.inds[ticker]["roc"], period=10, plot=False, subplot=False)
            # self.inds[ticker]["roc_std_sma10"] = bt.indicators.EMA(self.inds[ticker]["roc_std"], period=10, plot=False, subplot=False)
            # self.inds[ticker]["roc_std_sma20"] = bt.indicators.EMA(self.inds[ticker]["roc_std"], period=20, plot=False, subplot=False)
            # self.inds[ticker]["roc_std_sma20"].plotinfo.plotmaster = self.inds[ticker]["roc_std_sma10"]
            # self.inds[ticker]["roc_std_sma50"] = bt.indicators.EMA(self.inds[ticker]["roc_std"], period=50, plot=False, subplot=False)
            # self.inds[ticker]["roc_std_sma50"].plotinfo.plotmaster = self.inds[ticker]["roc_std_sma10"]
            # self.inds[ticker]["roc_std_sma200"] = bt.indicators.EMA(self.inds[ticker]["roc_std"], period=200, plot=False, subplot=False)
            # self.inds[ticker]["roc_std_sma200"].plotinfo.plotmaster = self.inds[ticker]["roc_std_sma10"]

            # self.inds[ticker]["st_5m"] = SuperTrend(d, plot=True)
        # for d in self.datas_1h:
        #     ticker = d._name
        #     ticker = ticker[3:]
        #     # self.inds[ticker]["rsi_1h"] = bt.indicators.RSI(d, plot=True, subplot=True)
        #     # self.inds[ticker]["adx_1h"] = bt.indicators.ADX(d, plot=True, subplot=True)
        #     # self.inds[ticker]["hh_1h"] = bt.indicators.Highest(d.high, plot=True, subplot=True)
        #     # self.inds[ticker]["ll_1h"] = bt.indicators.Lowest(d.low, plot=True, subplot=True)
        #     # self.inds[ticker]["atr_1h"] = bt.indicators.ATR(d, plot=True, subplot=True)
        #     self.inds[ticker]["sma5_1h"] = bt.indicators.EMA(d.close, period=5, plot=True, subplot=False)
        #     self.inds[ticker]["sma20_1h"] = bt.indicators.EMA(d.close, period=20, plot=True, subplot=False)
        #     # self.inds[ticker]["sma50_1h"] = bt.indicators.EMA(d.close, period=50, plot=True, subplot=False)
        #     # self.inds[ticker]["st_1h"] = SuperTrend(d, plot=True)

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
            # self.datas_5m.sort(reverse=True, key=lambda d: (self.inds[d._name[3:]]["rsi_5m"][0] * self.inds[d._name[3:]]["adx_5m"][0]) * (self.inds[d._name[3:]]["roc"][0]))
            # self.datas_5m.sort(reverse=True, key=lambda d: abs(self.inds[d._name[3:]]["pct_change"][0]) * abs(self.inds[d._name[3:]]["volsma_slow_5m"][0]))
            # self.datas_5m.sort(reverse=True, key=lambda d: abs(self.inds[d._name[3:]]["volsma_slow_5m"][0]))
            self.datas_5m.sort(reverse=True, key=lambda d: abs(self.inds[d._name]["pct_change"][0]))
            for d in self.datas_5m:
                ticker = d._name
                # ticker = ticker[3:]
                current_position = self.get_position(d=d, attribute='size')
                # if current_position > 0:
                #     if self.stop_order:
                #         self.cancel(self.stop_order)
                #     self.stop_order = self.close(d, exectype=bt.Order.StopTrail, trailamount=self.inds[ticker]["ll_5m"][0])
                # elif current_position < 0:
                #     if self.inds[ticker]["roc_std_sma10"][-1] > self.inds[ticker]["roc_std_sma20"][-1] and self.inds[ticker]["roc_std_sma10"][0] < self.inds[ticker]["roc_std_sma20"][0]:
                #         self.order_target_percent(d, target=0)
                #     if self.stop_order:
                #         self.cancel(self.stop_order)
                #     self.stop_order = self.close(d, exectype=bt.Order.StopTrail, trailamount=self.inds[ticker]["hh_5m"][-1])

                self.pos[ticker]["size"] = self.get_position(d=d, attribute='size')
                self.pos[ticker]["price"] = self.get_position(d=d, attribute='price')
                if current_position > 0:
                    # StopWin
                    self.pos[ticker]["profit"] = d.close[0] - self.pos[ticker]["price"]
                    self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker][
                        "price"]) * 100
                    self.pos[ticker]["profit_-1"] = d.close[-1] - self.pos[ticker]["price"]
                    self.pos[ticker]["profit_percentage_-1"] = (self.pos[ticker]["profit_-1"] / self.pos[ticker][
                        "price"]) * 100
                    self.log(f'{ticker} {self.pos[ticker]["profit_percentage"]}')
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
                    #     self.pos[ticker]["new_sl_price"] = self.inds[ticker]["ll_fastest_5m"][0]
                    # elif self.pos[ticker]["profit_percentage"] > 15:
                    #     self.pos[ticker]["new_sl_price"] = self.inds[ticker]["ll_fast_5m"][0]
                    # elif self.pos[ticker]["profit_percentage"] > 5:
                    #     self.pos[ticker]["new_sl_price"] = self.inds[ticker]["ll_5m"][0]
                    if self.pos[ticker]["new_sl_price"] and self.pos[ticker]["sl_price"] and self.pos[ticker]["new_sl_price"] > self.pos[ticker]["sl_price"]:
                        self.log(
                            f'{ticker} LONG Update stop from {self.pos[ticker]["sl_price"]} to {self.pos[ticker]["new_sl_price"]}')
                        self.pos[ticker]["sl_price"] = self.pos[ticker]["new_sl_price"]
                        if (ticker in self.stop_order) and (self.stop_order[ticker] is not None):
                            self.cancel(self.stop_order[ticker])
                            self.stop_order[ticker] = None
                        self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)

                if current_position < 0:
                    # StopWin
                    self.pos[ticker]["profit"] = self.pos[ticker]["price"] - d.close[0]
                    self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker][
                        "price"]) * 100
                    # if self.pos[ticker]["profit_percentage"] > 95:
                    #     # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                    #     self.pos[ticker]["new_sl_price"] = 0.555 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 85:
                    #     # self.log(f'{ticker} Long profit > 85%')
                    #     self.pos[ticker]["new_sl_price"] = 0.588 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 75:
                    #     # self.log(f'{ticker} Long profit > 75%')
                    #     self.pos[ticker]["new_sl_price"] = 0.625 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 65:
                    #     # self.log(f'{ticker} Long profit > 65%')
                    #     self.pos[ticker]["new_sl_price"] = 0.67 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 55:
                    #     # self.log(f'{ticker} Long profit > 55%')
                    #     self.pos[ticker]["new_sl_price"] = 0.71 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 45:
                    #     # self.log(f'{ticker} Long profit > 45%')
                    #     self.pos[ticker]["new_sl_price"] = 0.77 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 35:
                    #     # self.log(f'{ticker} Long profit > 35%')
                    #     self.pos[ticker]["new_sl_price"] = 0.83 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 25:
                    #     # self.log(f'{ticker} Long profit > 25%')
                    #     self.pos[ticker]["new_sl_price"] = 0.9 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 15:
                    #     # self.log(f'{ticker} Long profit > 15%')
                    #     self.pos[ticker]["new_sl_price"] = 0.95 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 5:
                    #     # self.log(f'{ticker} Long profit > 5')
                    #     self.pos[ticker]["new_sl_price"] = 1 * self.pos[ticker]["price"]
                    if self.pos[ticker]["profit_percentage"] > self.inds[ticker]["volatility_5m"][0]*25:
                        self.log(f'{ticker} Short profit > 25')
                        self.pos[ticker]["new_sl_price"] = self.inds[ticker]["hh_fastest_5m"][0]
                    elif self.pos[ticker]["profit_percentage"] > self.inds[ticker]["volatility_5m"][0]*15:
                        self.log(f'{ticker} Short profit > 15')
                        self.pos[ticker]["new_sl_price"] = self.inds[ticker]["hh_fast_5m"][0]
                        # self.pos[ticker]["new_sl_price"] = (1 + ((self.pos[ticker]["profit_percentage"]+4)*0.01)) * 1 * self.pos[ticker]["price"]
                    elif self.pos[ticker]["profit_percentage"] > self.inds[ticker]["volatility_5m"][0]*5:
                        self.log(f'{ticker} Short profit > 5')
                        self.pos[ticker]["new_sl_price"] = self.inds[ticker]["hh_5m"][0]
                        # self.pos[ticker]["new_sl_price"] = (1 + ((self.pos[ticker]["profit_percentage"]+5)*0.01)) * 1 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] < 5:
                    #     self.sell(d, size=abs(self.pos[ticker]["size"])/2)
                    if self.pos[ticker]["new_sl_price"] and self.pos[ticker]["sl_price"] and self.pos[ticker]["new_sl_price"] < self.pos[ticker]["sl_price"]:
                        self.log(
                            f'{ticker} SHORT Update stop from {self.pos[ticker]["sl_price"]} to {self.pos[ticker]["new_sl_price"]}')
                        self.pos[ticker]["sl_price"] = self.pos[ticker]["new_sl_price"]
                        if (ticker in self.stop_order) and (self.stop_order[ticker] is not None):
                            self.cancel(self.stop_order[ticker])
                            self.stop_order[ticker] = None
                        self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)

                if current_position > 0:
                    if self.inds[ticker]["sma50_5m"][0] < self.inds[ticker]["sma100_5m"][0]:
                        self.close(d)
                elif current_position < 0:
                    if self.inds[ticker]["sma50_5m"][0] > self.inds[ticker]["sma100_5m"][0]:
                        self.close(d)

            # TO OPEN POSITIONS ONLY IN TOP RANKED COINS, UNCOMMENT BLOCK BELOW
            # for d in self.datas_5m[0:7]:
            #     ticker = d._name
            #     current_position = self.get_position(d=d, attribute='size')
                if current_position == 0:
                    if (ticker in self.stop_order) and (self.stop_order[ticker] is not None):
                        self.cancel(self.stop_order[ticker])
                        self.stop_order[ticker] = None
                    self.pos[ticker]["price"] = None
                    if self.inds[ticker]["sma20_5m"][0] > self.inds[ticker]["sma50_5m"][0] > self.inds[ticker]["sma100_5m"][0] > self.inds[ticker]["sma240_5m"][0]:  # look for longs
                        self.entry_order[ticker] = self.add_order(d, target=((self.p.order_target_percent / 100) * self.inds[ticker]["volatility_5m"][0]))
                        # self.entry_order[ticker] = self.order_target_percent(d, target=((self.p.order_target_percent / 100) * self.inds[ticker]["volatility_5m"][0])*0.67, price=d.close[0]-self.inds[ticker]["atr_5m"][0]/3, exectype=bt.Order.Limit)
                        self.pos[ticker]["sl_price"] = 0.5 * d.close[0]
                        self.pos[ticker]["new_sl_price"] = None
                    elif self.inds[ticker]["sma20_5m"][0] < self.inds[ticker]["sma50_5m"][0] < self.inds[ticker]["sma100_5m"][0] < self.inds[ticker]["sma240_5m"][0]:  # look for longs
                        self.entry_order[ticker] = self.add_order(d, target=-((self.p.order_target_percent / 100) * self.inds[ticker]["volatility_5m"][0]))
                        # self.entry_order[ticker] = self.order_target_percent(d, target=-((self.p.order_target_percent / 100) * self.inds[ticker]["volatility_5m"][0])/2, price=d.close[0]+self.inds[ticker]["atr_5m"][0]/2)
                        self.pos[ticker]["sl_price"] = 2 * d.close[0]
                        self.pos[ticker]["new_sl_price"] = None
                    # elif d.close[0] < self.inds[ticker]["sma240_5m"][0] and d.close[0] < self.inds[ticker]["st_5m"][0]:  # look for shorts:
                    #     if ticker in self.entry_order:
                    #         self.cancel(self.entry_order[ticker])
                    #     self.entry_order[ticker] = self.order_target_percent(d, target=-((self.p.order_target_percent / 100) * self.inds[ticker]["volatility_5m"][0]), price=self.inds[ticker]["sma240_5m"][0], exectype=bt.Order.Limit)
                    #     self.pos[ticker]["sl_price"] = 1.5 * d.close[0]
                    #     self.pos[ticker]["new_sl_price"] = None
                    # self.order_target_percent(d, target=0.25)
                # elif d.high[0] < self.inds[ticker]["sma5_1h"][0] < self.inds[ticker]["sma20_1h"][0] and d.high[0] < self.inds[ticker]["sma20_5m"][0]:
                # elif d.high[0] < self.inds[ticker]["sma60_5m"][0] < self.inds[ticker]["sma240_5m"][0] and d.high[0] < self.inds[ticker]["sma20_5m"][0]:
                #     volatility = self.inds[ticker]["atr_5m"][0] / d.high[0]
                #     volatility_factor = 1 / (volatility * 100)
                #     self.add_order(d, target=-((self.p.order_target_percent / 100) * volatility_factor), type="market")
                #     self.pos[ticker]["sl_price"] = 10 * d.close[0]
                #     self.pos[ticker]["new_sl_price"] = None

            if self.to_place_orders is not None and len(self.to_place_orders) > 0:
                print(self.to_place_orders)
                order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                for order_chunk in order_chunks:
                    self.placed_orders = self.place_batch_order(order_chunk)

            for i, d in enumerate(self.datas_5m):
                ticker = d._name
                if self.placed_orders is not None:
                    for placed_order in self.placed_orders:
                        if placed_order.ccxt_order["symbol"] == ticker:
                            # Only remember the most recently placed order for a ticker, TODO: improve soon
                            self.orders[ticker] = placed_order
