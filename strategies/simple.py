import backtrader as bt
from indicators.swing import Swing


class simpleStrategy(bt.Strategy):
    def __init__(self):
        self.piv = Swing(period=7)