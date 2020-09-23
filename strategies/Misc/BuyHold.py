import argparse
import datetime

import backtrader as bt
from strategies.base import StrategyBase

class BuyAndHold_Buy(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('random_param', 20)
    )
    def __init__(self):
        StrategyBase.__init__(self)

    def start(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def nextstart(self):
        # Buy all the available cash
        size = int(self.broker.get_cash() / self.data)
        self.order = self.exec_trade(direction="buy", exectype=self.params.exectype, size=size)

class BuyAndHold_Target(StrategyBase):
    def __init__(self):
        StrategyBase.__init__(self)

    def start(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def nextstart(self):
        # Buy all the available cash
        size = int(self.broker.get_cash() / self.data)
        self.order = self.exec_trade(direction="buy", exectype=self.params.exectype, size=size)

class BuyAndHold_More(StrategyBase):
    params = dict(
        monthly_cash=1000.0,  # amount of cash to buy every month
    )

    def __init__(self):
        StrategyBase.__init__(self)
        
    def start(self):
        self.cash_start = self.broker.get_cash()
        self.val_start = 100.0

        # Add a timer which will be called on the 1st trading day of the month
        self.add_timer(
            bt.timer.SESSION_END,  # when it will be called
            monthdays=[1],  # called on the 1st day of the month
            monthcarry=True,  # called on the 2nd day if the 1st is holiday
        )

    def notify_timer(self, timer, when, *args, **kwargs):
        # Add the influx of monthly cash to the broker
        self.broker.add_cash(self.p.monthly_cash)

        # buy available cash
        target_value = self.broker.get_value() + self.p.monthly_cash
        self.order_target_value(target=target_value)


class BuyAndHold_More_Fund(StrategyBase):
    params = dict(
        monthly_cash=1000.0,  # amount of cash to buy every month
    )
    
    def __init__(self):
        StrategyBase.__init__(self)

    def start(self):
        # Activate the fund mode and set the default value at 100
        self.broker.set_fundmode(fundmode=True, fundstartval=100.00)

        self.cash_start = self.broker.get_cash()
        self.val_start = 100.0

        # Add a timer which will be called on the 1st trading day of the month
        self.add_timer(
            bt.timer.SESSION_END,  # when it will be called
            monthdays=[1],  # called on the 1st day of the month
            monthcarry=True,  # called on the 2nd day if the 1st is holiday
        )

    def notify_timer(self, timer, when, *args, **kwargs):
        # Add the influx of monthly cash to the broker
        self.broker.add_cash(self.p.monthly_cash)

        # buy available cash
        target_value = self.broker.get_value() + self.p.monthly_cash
        self.order_target_value(target=target_value)