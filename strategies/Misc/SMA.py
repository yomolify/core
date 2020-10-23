import backtrader as bt
import datetime
from strategies.base import StrategyBase

class SMA(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('modbuy', 2),
        ('modsell', 3),
    )
    # ('period_sma', 10),

    def __init__(self):
        StrategyBase.__init__(self)
        self.stop_order = None
        self.cancel_order = None
        # self.sma = bt.ind.SMA(
        #     period=self.params.period_sma, plot=True)

        # self.buy_sig = bt.ind.CrossUp(self.datas[0].close, self.sma)
        # self.close_sig = bt.ind.CrossDown(self.datas[0].close, self.sma)

    # Strategy for easy realistic testing

    # def next(self):
    #     # Check if an order is pending ... if yes, we cannot send a 2nd one
    #     if self.order:
    #         return
    #     # Check if we are in the market
    #     # if not self.position:
    #     if abs(self.broker.getposition(self.datas[0]).size) < 0.01:
    #         if self.buy_sig:
    #             self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
            
    #     elif abs(self.broker.getposition(self.datas[0]).size) > 0.01:
    #         if self.close_sig:
    #             self.order = self.exec_trade(direction="close", exectype=self.params.exectype)
    
    # Places buy and close on alternate bars for fast testing
    def next(self):
        pos = len(self.data)
        if pos % self.params.modbuy == 0:
            # if abs(self.broker.getposition(self.datas[0]).size) < 0.01:
            # self.long_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
            self.stop_order = self.exec_trade(direction="sell", price=self.datas[0].close*0.6, exectype=bt.Order.Stop)
            print('self.stop_order after placing stop')
            print(self.stop_order)
            print('self.cancel_order after placing stop')
            print(self.cancel_order)

        if pos % self.params.modbuy != 0:
            # if self.broker.getposition(self.datas[0]).size > 0:
            # self.short_order = self.exec_trade(direction="sell", exectype=self.params.exectype)
            if self.stop_order:
                self.cancel_order = self.cancel(self.stop_order)
                print('self.stop_order after placing cancel')
                print(self.stop_order)
                print('self.cancel_order after placing cancel')
                print(self.cancel_order)
