import backtrader as bt
import datetime
from strategies.base import StrategyBase


class Breakout(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),

    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.buy_order = None
        self.sell_order = None
        self.adx = bt.ind.ADX(plot=True)
        self.highest_high = bt.ind.Highest(
            period=10, plot=False)
        self.lowest_low = bt.ind.Lowest(
            period=10, plot=False)

    def next(self):
        if self.
        if self.adx < 20:
            self.buy_order = self.buy(exectype=bt.Order.Stop, price=self.highest_high[0])
            self.sell_order = self.sell(exectype=bt.Order.Stop, price=self.lowest_low[0])