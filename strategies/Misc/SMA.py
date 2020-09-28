import backtrader as bt
import datetime
from strategies.base import StrategyBase

class SMA(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('period_sma', 10),
        ('modbuy', 2),
        ('modsell', 3),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.sma = bt.ind.SMA(
            period=self.params.period_sma, plot=True)

        # self.buy_sig = self.datas.close > self.sma
        # self.sell_sig = self.data.close < self.sma
        
        self.buy_sig = bt.ind.CrossUp(self.datas[0].close, self.sma)
        self.close_sig = bt.ind.CrossDown(self.datas[0].close, self.sma)

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        self.log('{}'.format(self.position), color='magenta', send_telegram=True)
        # Check if we are in the market
        # if not self.position:
        if abs(self.broker.getposition(self.datas[0]).size) < 0.01:
            if self.buy_sig:
                self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
            
        elif abs(self.broker.getposition(self.datas[0]).size) > 0.01:
            if self.close_sig:
                self.order = self.exec_trade(direction="close", exectype=self.params.exectype)