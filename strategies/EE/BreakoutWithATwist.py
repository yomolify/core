import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT

class BreakoutWithATwist(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_rolling_high', 500),
        ('period_rolling_low', 500),
        ('period_sma_bitcoin', 250),
        ('period_sma_veryfast', 10),
        ('period_sma_fast', 20),
        ('period_sma_mid', 50),
        ('period_sma_slow', 200),
        ('period_sma_veryslow', 500),
        ('period_sma_veryslow', 500),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        ('order_target_percent', 5)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.orders = dict()
        self.buy_order = dict()
        self.sell_order = dict()
        self.buy_stop_order = dict()
        self.sell_stop_order = dict()
        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            self.buy_order[ticker] = None
            self.sell_order[ticker] = None
            self.buy_stop_order[ticker] = None
            self.sell_stop_order[ticker] = None
            self.inds[ticker] = {}
            self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high, plot=False, subplot=False)
            self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low, plot=False, subplot=False)
            self.inds[ticker]["average_true_range"] = bt.indicators.AverageTrueRange(d, plot=False)
            self.inds[ticker]["sma_veryfast"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_veryfast, plot=False)
            self.inds[ticker]["sma_fast"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_fast, plot=False)
            self.inds[ticker]["sma_mid"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_mid, plot=False)
            self.inds[ticker]["sma_slow"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_slow, plot=False)
            self.inds[ticker]["sma_veryslow"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_veryslow, plot=False)
            self.inds[ticker]["sma_highs"] = bt.ind.SimpleMovingAverage(d.high,
                period=self.params.period_sma_highs, plot=False)
            self.inds[ticker]["sma_lows"] = bt.ind.SimpleMovingAverage(d.low,
                period=self.params.period_sma_lows, plot=False)
            self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=False)
            self.inds[ticker]["adx_15"] = bt.ind.ADX(d, period=15, plot=True)
            self.inds[ticker]["adx_20"] = bt.ind.ADX(d, period=20, plot=True)
            self.inds[ticker]["sma_adx_20"] = bt.ind.HMA(self.inds[ticker]["adx_20"], period=20, plot=True, subplot=True)
            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)
            self.inds[ticker]["highest_high"] = bt.ind.Highest(
                period=10, plot=False)
            self.inds[ticker]["lowest_low"] = bt.ind.Lowest(
                period=10, plot=False)

    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            available = list(filter(lambda d: len(d) > 500, self.altcoins))
            for i, d in enumerate(available):
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                if current_position > 0:
                    self.cancel(self.sell_order[ticker])
                    self.cancel(self.buy_order[ticker])
                    # self.cancel(self.buy_stop_order[ticker])
                    # self.buy_stop_order[ticker] = self.close(exectype=bt.Order.Stop, price=d.close[-1] - self.inds[ticker]["average_true_range"][-1])
                    # if d.high[0] < d.high[-1]:
                    #     self.close()
                    if self.inds[ticker]["adx_15"][0] > 25 and self.inds[ticker]["sma_adx_20"][-1] > self.inds[ticker]["sma_adx_20"][0]:
                        self.close()
                    elif self.inds[ticker]["adx_15"][0] < 20:
                        self.sell_order[ticker] = self.close(exectype=bt.Order.Stop, price=self.inds[ticker]["lowest_low"][0])
                elif current_position < 0:
                    self.cancel(self.sell_order[ticker])
                    self.cancel(self.buy_order[ticker])
                    if self.inds[ticker]["adx_15"][0] < 20:
                        self.sell_order[ticker] = self.close(exectype=bt.Order.Stop, price=self.inds[ticker]["highest_high"][0])
                if current_position == 0:
                    if self.buy_order[ticker]:
                        self.cancel(self.buy_order[ticker])
                        self.buy_order[ticker] = None
                    if self.sell_order[ticker]:
                        self.cancel(self.sell_order[ticker])
                        self.sell_order[ticker] = None
                    if self.buy_stop_order[ticker]:
                        self.cancel(self.buy_stop_order[ticker])
                        self.buy_stop_order[ticker] = None
                    if self.sell_stop_order[ticker]:
                        self.cancel(self.sell_stop_order[ticker])
                        self.sell_stop_order[ticker] = None
                    if self.inds[ticker]["adx_15"][0] < 20:
                        self.buy_order[ticker] = self.buy(exectype=bt.Order.Stop, price=self.inds[ticker]["highest_high"][0])
                        self.sell_order[ticker] = self.sell(exectype=bt.Order.Stop, price=self.inds[ticker]["lowest_low"][0])
