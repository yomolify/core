import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase


class HundredDayBreakout(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_rolling_high', 1000),
        ('period_rolling_low', 1000),
        ('period_sma_bitcoin', 200),
        ('order_target_percent', 0.05)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas[1:]
        self.inds = {}
        self.orders = dict()

        self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close,
                                                            period=self.params.period_sma_bitcoin)

        for d in self.datas:
            ticker = d._name
            self.inds[ticker] = {}
            self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high, plot=True, subplot=False)
            self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low, plot=True, subplot=False)

    def next(self):
        available = list(filter(lambda d: len(d), self.altcoins))
        for i, d in enumerate(available):
            ticker = d._name
            current_position = self.getposition(d).size
            self.log('{} Position {}'.format(ticker, current_position))
            if current_position > 0:
                if (self.bitcoin.close[0] < self.bitcoin_sma[0]) or (d.low[0] < self.inds[ticker]['rolling_low'][-1]):
                    order = self.order_target_percent(data=d, target=0)
                    self.orders[ticker].append(order)
            if current_position == 0:
                if self.bitcoin.close[0] > self.bitcoin_sma[0]:
                    if d.close[0] > self.inds[ticker]['rolling_high'][-1]:
                        self.orders[ticker] = [self.order_target_percent(data=d, target=self.p.order_target_percent)]
                        self.log('{} Buy initiated {}'.format(ticker, self.orders[ticker][0]))