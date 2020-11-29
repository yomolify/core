import backtrader as bt
import numpy as np
from strategies.base import StrategyBase
import sys
import talib


class Correlation(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('correlation', 20),  # only for pct change, not for volatility
        ('order_target_percent', 0.5),  # only for pct change, not for volatility
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.inds = {}
        self.correlation = bt.talib.CORREL(self.data0, self.data1)
        for d in self.datas:
            self.inds[d] = {}
            self.inds[d]["pct"] = bt.indicators.PercentChange(d.close, period=1)
        #     self.inds[d]["std"] = bt.indicators.StandardDeviation(d.close, period=200)

    def next(self):
        if self.i % 1 == 0:
            self.rebalance_portfolio()
        self.i += 1

    def rebalance_portfolio(self):
        if self.correlation > 0.8:
            if self.inds[self.data0]["pct"][0] > self.inds[self.data1]["pct"][0]:
                self.log('long 1, short 0')
                cash = self.broker.get_cash()
                size = (cash/self.data1.close[0])/5
                self.log(f'size {size}')
                self.buy(data=self.data1, size=size)
            else:
                self.log('long 0, short 1')
                self.close(data=self.data1)

            # if self.inds[self.data0]["pct"][0] > self.inds[self.data1]["pct"][0]:
            #     self.log('long 1, short 0')
            #     self.order_target_percent(data=self.data1, target=self.p.order_target_percent)
            # elif self.inds[self.data1]["pct"][0] > self.inds[self.data0]["pct"][0]:
            #     self.log('long 0, short 1')
            #     self.order_target_percent(data=self.data0, target=self.p.order_target_percent)



