import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase


class TurtleTrader(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_s1_entry', 20),
        ('period_s1_exit', 10),
        ('period_s2_entry', 55),
        ('period_s2_exit', 20),
        ('order_target_percent', 0.02),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.indicators = {}
        self.orders = dict()

        for d in self.datas:
            ticker = d._name
            self.indicators[ticker] = {}
            self.indicators[ticker]["s1_entry"] = bt.indicators.Highest(d.high, period=self.params.period_s1_entry, plot=True, subplot=False)
            self.indicators[ticker]["s1_exit"] = bt.indicators.Lowest(d.low, period=self.params.period_s1_exit, plot=True, subplot=False)
            self.indicators[ticker]["s2_entry"] = bt.indicators.Lowest(d.low, period=self.params.period_s2_entry, plot=True, subplot=False)
            self.indicators[ticker]["s2_exit"] = bt.indicators.Lowest(d.low, period=self.params.period_s2_exit, plot=True, subplot=False)

    def next(self):
        # TODO - Filter trades that where previous breakout was a success in S1 they should be only taken if S2 hits
        # TODO - Try close instead of high

        available = list(filter(lambda d: len(d), self.datas))
        for i, d in enumerate(available):
            ticker = d._name
            current_position = self.getposition(d).size
            self.log('{} Position {}'.format(ticker, current_position))
            if current_position > 0:
                # LONG EXIT S1 & S2
                if (d.low[0] < self.indicators[ticker]['s1_exit'][-1]) or (d.low[0] < self.indicators[ticker]['s2_exit'][-1]):
                    order = self.order_target_percent(data=d, target=0)
                    self.orders[ticker].append(order)
            if current_position == 0:
                # LONG ENTRY S1 & S2
                if (d.high[0] > self.indicators[ticker]['s1_entry'][-1]) or (d.high[0] > self.indicators[ticker]['s2_entry'][-1]):
                    self.orders[ticker] = [self.order_target_percent(data=d, target=self.p.order_target_percent)]
                    self.log('{} Buy initiated {}'.format(ticker, self.orders[ticker][0]))
