import backtrader as bt
import numpy as np
from strategies.base import StrategyBase
import sys

def min_n(array, n):
    return np.argpartition(array, n)[:n]


def max_n(array, n):
    return np.argpartition(array, -n)[-n:]


class CrossSectional(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('num_positions', 35),  # only for pct change, not for volatility
        ('n', 35), # volatility
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.inds = {}
        for d in self.datas:
            self.inds[d] = {}
            self.inds[d]["pct"] = bt.indicators.PercentChange(d.close, period=50)
            self.inds[d]["std"] = bt.indicators.StandardDeviation(d.close, period=200)

    def prenext(self):
        self.next()

    def next(self):
        if self.i % 1 == 0:
            self.rebalance_portfolio()
        self.i += 1

    def rebalance_portfolio(self):
        available = list(filter(lambda d: len(d) > 200, self.datas))  # only look at data that existed last week
        rets = np.zeros(len(available))
        stds = np.zeros(len(available))
        for i, d in enumerate(available):
            rets[i] = self.inds[d]['pct'][0]
            stds[i] = self.inds[d]['std'][0]

        market_ret = np.mean(rets)
        weights = -(rets - market_ret)
        max_weights_index = max_n(np.abs(weights), self.params.num_positions)
        low_volality_index = min_n(stds, self.params.n)
        selected_weights_index = np.intersect1d(max_weights_index,
                                                low_volality_index)
        if not len(selected_weights_index):
            # no good trades today
            return

        selected_weights = weights[selected_weights_index]
        weights = weights / np.sum(np.abs(selected_weights))
        for i, d in enumerate(available):
            try:
                if i in selected_weights_index:
                    self.order_target_percent(d, target=weights[i])
                else:
                    self.order_target_percent(d, 0)
            except Exception as e:
                self.log("CSMR ERROR: {}".format(sys.exc_info()[0]))
                self.log("{}".format(e))

        #
        # available = list(filter(lambda d: len(d), self.datas))  # only look at data that existed yesterday
        # rets = np.zeros(len(available))
        # for i, d in enumerate(available):
        #     rets[i] = self.inds[d]['pct'][0]
        #
        # market_ret = np.mean(rets)
        # weights = -(rets - market_ret)
        # max_weights_index = max_n(np.abs(weights), self.params.num_positions)
        # max_weights = weights[max_weights_index]
        # weights = weights / np.sum(np.abs(max_weights))
        #
        # for i, d in enumerate(available):
        #     try:
        #         if i in max_weights_index:
        #             self.order_target_percent(d, target=weights[i])
        #         else:
        #             self.order_target_percent(d, 0)
        #     except Exception as e:
        #         self.log("ERROR: {}".format(sys.exc_info()[0]))
        #         self.log("{}".format(e))


        # No Filter
        # only look at data that existed yesterday
        # available = list(filter(lambda d: len(d), self.datas))
        #
        # rets = np.zeros(len(available))
        # for i, d in enumerate(available):
        #     # calculate individual daily returns
        #     # rets[i] = (d.close[0] - d.close[-1]) / d.close[-1]
        #     rets[i] = self.inds[d]['pct'][0]
        #
        # # calculate weights using formula
        # market_ret = np.mean(rets)
        # weights = -(rets - market_ret)
        # weights = weights / np.sum(np.abs(weights))
        #
        # for i, d in enumerate(available):
        #     self.order_target_percent(d, target=weights[i])
