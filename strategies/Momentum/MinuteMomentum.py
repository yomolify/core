import collections
from strategies.base import StrategyBase

import backtrader as bt
from backtrader.indicators import MovingAverageSimple

from indicators.Momentum import Momentum


class MinuteMomentum(StrategyBase):

    params = dict(
        exectype=bt.Order.Market,
        momentum=Momentum,
        momentum_period=10,
        vol_period=20,
        minimum_momentum=40,
        reserve=0.05,
        maximum_stake=0.2,
        trail=False,
        stop_loss=0.02
    )

    def __init__(self):
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
        self.strategy = None
        self.entry_bar_height = None
        self.to_place_orders = []
        self.first_bar_after_entry = dict()
        self.sma = bt.ind.SMA(self.data, period=self.p.vol_period)
        self.momentum = self.p.momentum(self.sma, period=self.p.momentum_period)
        pct_change = bt.ind.PctChange(self.sma, period=self.p.vol_period)
        self.volatility = bt.ind.StdDev(pct_change, period=self.p.vol_period)

    def next(self):
        cash = self.broker.get_cash()

        if cash <= 0:
            return

        if self.momentum > 40:
            self.order_target_percent(self.data, target=self.calculate_target_weight(), symbol=self.data._name)

    def calculate_target_weight(self):
        weight = 1 / (self.momentum * self.volatility)
        return weight / (weight + self.p.reserve)
    #
    # def notify_order(self, order):
    #     if order.alive():
    #         return
    #
    #     otypetxt = 'Buy' if order.isbuy() else 'Sell'
    #     if order.status == order.Completed:
    #         self.log(
    #             '{} Order Completed - Symbol: {} Size: {} @Price: {} Value: {:.2f} Comm: {:.2f}'.format(
    #                 otypetxt, order.info['symbol'], order.executed.size, order.executed.price,
    #                 order.executed.value, order.executed.comm
    #             ))
    #     else:
    #         self.log('{} Order rejected'.format(otypetxt))
    #
    # def log(self, arg):
    #     print(f'{self.datetime.date(), arg}')
