import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase


class NewYearlyHighs(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_rolling_high', 500),
        ('period_rolling_low', 500),
        ('period_sma_bitcoin', 100),
        ('period_highest_high_slow', 20),
        ('period_highest_high_mid', 10),
        ('period_highest_high_fast', 5),
        ('order_target_percent', 0.2)
        # ('order_target_percent', 0.05)
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
        # self.rolling_high = bt.ind.Highest(
        #     period=self.params.period_rolling_high, plot=True)
        # self.rolling_low = bt.ind.Lowest(
        #     period=self.params.period_rolling_low, plot=True)
        # self.highest_high_slow = bt.ind.Highest(
        #     period=self.params.period_highest_high_slow, plot=False)
        # self.highest_high_mid = bt.ind.Highest(
        #     period=self.params.period_highest_high_mid, plot=False)
        # self.highest_high_fast = bt.ind.Highest(
        #     period=self.params.period_highest_high_fast, plot=False)

        # cross_up_rolling_high = bt.ind.CrossUp(self.datas[0].close, self.rolling_high)
        # cross_down_rolling_low = bt.ind.CrossDown(self.datas[0].close, self.rolling_low)
        #
        # self.buy_sig = cross_up_rolling_high
        # self.close_sig = cross_down_rolling_low

    # def update_indicators(self):
    #     self.profit = 0
    #     if self.position.size > 0:
    #         self.profit = self.data0.close[0] - self.buy_price_close
    #         self.profit_percentage = (self.profit / self.buy_price_close) * 100
    #         if (self.profit_percentage > 45):
    #             self.log('IN >45')
    #             self.new_sl_price = 1.40 * self.buy_price_close
    #         if (self.profit_percentage > 40):
    #             self.log('IN >40')
    #             self.new_sl_price = 1.35 * self.buy_price_close
    #         elif (self.profit_percentage > 35):
    #             self.log('IN >35')
    #             self.new_sl_price = 1.30 * self.buy_price_close
    #         elif (self.profit_percentage > 30):
    #             self.log('IN >30')
    #             self.new_sl_price = 1.25 * self.buy_price_close
    #         elif (self.profit_percentage > 25):
    #             self.log('IN >25')
    #             self.new_sl_price = 1.20 * self.buy_price_close
    #         elif (self.profit_percentage > 20):
    #             self.log('IN >20')
    #             self.new_sl_price = 1.15 * self.buy_price_close
    #         if self.new_sl_price and self.sl_price and self.new_sl_price > self.sl_price:
    #             self.log('better long stop')
    #             self.sl_price = self.new_sl_price
    #             if (self.long_stop_order):
    #                 self.cancel(self.long_stop_order)
    #             self.long_stop_order = self.exec_trade(direction="close", price=self.sl_price, exectype=bt.Order.Stop)
    #     elif self.position.size < 0:
    #         self.new_sl_price = self.highest_high_slow[0]
    #         self.profit = self.sell_price_close - self.data0.close[0]
    #         self.profit_percentage = (self.profit / self.sell_price_close) * 100
    #         if (self.profit_percentage > 40):
    #             self.log('IN >40')
    #             self.new_sl_price = 0.65 * self.sell_price_close
    #         if (self.profit_percentage > 35):
    #             self.log('IN >35')
    #             self.new_sl_price = 0.7 * self.sell_price_close
    #         elif (self.profit_percentage > 30):
    #             self.log('IN > 30')
    #             self.new_sl_price = 0.75 * self.sell_price_close
    #         elif (self.profit_percentage > 25):
    #             self.log('IN > 25')
    #             self.new_sl_price = 0.8 * self.sell_price_close
    #         elif self.profit_percentage > 15:
    #             self.log('IN > 15')
    #             self.new_sl_price = self.highest_high_fast[0]
    #         elif self.profit_percentage > 10:
    #             self.log('IN > 10')
    #             self.new_sl_price = self.highest_high_mid[0]
    #         if self.new_sl_price and self.sl_price and self.new_sl_price < self.sl_price:
    #             self.log('better short stop')
    #             self.sl_price = self.new_sl_price
    #             if (self.short_stop_order):
    #                 self.cancel(self.short_stop_order)
    #             self.short_stop_order = self.exec_trade(direction="close", price=self.sl_price, exectype=bt.Order.Stop)

    def next(self):
        available = list(filter(lambda d: len(d), self.altcoins))
        for i, d in enumerate(available):
            ticker = d._name
            current_position = self.getposition(d).size
            self.log('{} Position {}'.format(ticker, current_position))
            if current_position > 0:
                if (self.bitcoin.close[0] < self.bitcoin_sma[0]) or (d.close[0] < self.inds[ticker]['rolling_low'][-1]):
                    order = self.order_target_percent(data=d, target=0)
                    self.orders[ticker].append(order)
            if current_position == 0:
                if self.bitcoin.close[0] > self.bitcoin_sma[0]:
                    if d.close[0] > self.inds[ticker]['rolling_high'][-1]:
                        self.orders[ticker] = [self.order_target_percent(data=d, target=self.p.order_target_percent)]
                        self.log('{} Buy initiated {}'.format(ticker, self.orders[ticker][0]))
        #
        # if abs(self.broker.getposition(self.datas[0]).size) > 0.0005:
        #     if self.datas[0].close[0] < self.rolling_low[-1]:
        #         self.long_order = None
        #         self.tp_price = self.data0.close[0]
        #         self.log('close_sig')
        #         self.exec_trade(direction="close", exectype=self.params.exectype)
        #         # Cancel Stops
        #         if self.long_stop_order:
        #             self.log('Cancelling long stop order')
        #             self.cancel(self.long_stop_order)
        #             self.long_stop_order = None
        #         if self.short_stop_order:
        #             self.log('Cancelling short stop order')
        #             self.cancel(self.short_stop_order)
        #             self.short_stop_order = None
            # else:
            #     self.update_indicators()
        # if abs(self.broker.getposition(self.datas[0]).size) < 0.0005:
        #     if self.long_stop_order:
        #         self.log('Cancelling redundant long stop order')
        #         self.cancel(self.long_stop_order)
        #     self.long_order = None
        #     self.short_order = None
        #     self.long_stop_order = None
        #     self.short_stop_order = None
        #     self.sl_price = None
        #     self.new_sl_price = None
        #     self.tp_price = None

        # if self.long_order or self.short_order:
        #     return
        #
        # if abs(self.broker.getposition(self.datas[0]).size) < 0.0005:
        #     if self.datas[0].close[0] > self.rolling_high[-1]:
        #         self.long_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
