import backtrader as bt
import numpy as np
from strategies.base import StrategyBase

def min_n(array, n):
    return np.argpartition(array, n)[:n]


def max_n(array, n):
    return np.argpartition(array, -n)[-n:]


class CrossSectional(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('n', 10),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.inds = {}
        for d in self.datas:
            self.inds[d] = {}
            self.inds[d]["pct"] = bt.indicators.PercentChange(d.close, period=5)
            self.inds[d]["std"] = bt.indicators.StandardDeviation(d.close, period=5)

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
        # print(weights)
        # print(np.abs(weights))
        # print(np.sum(np.abs(weights)))
        weights = weights / np.sum(np.abs(weights))

        for i, d in enumerate(available):
            self.order_target_percent(d, target=weights[i])
