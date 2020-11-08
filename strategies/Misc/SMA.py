import backtrader as bt
import datetime
from strategies.base import StrategyBase
from config import DEVELOPMENT, BASE, QUOTE, ENV, PRODUCTION, DEBUG, TRADING
import sys

class SMA(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('modbuy', 4),
        ('modsell', 6),
        ('period_rolling_high', 10),
        ('period_rolling_low', 10),
        ('period_sma_bitcoin', 10),
        ('period_sma_veryfast', 10),
        ('period_sma_fast', 10),
        ('period_sma_mid', 10),
        ('period_sma_slow', 10),
        ('period_sma_veryslow', 10),
        ('period_vol_sma_fast', 10),
        ('period_vol_sma_slow', 10),
        ('period_bb_sma', 10),
        ('period_bb_std', 2),
        # ('period_highest_high_slow', 20),
        # ('period_highest_high_mid', 10),
        # ('period_highest_high_fast', 5),
        ('order_target_percent', 0.1)
        # ('order_target_percent', 2)
        # ('order_target_percent', 20)
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

        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.orders = dict()
        # self.bitcoin_atr = bt.indicators.AverageTrueRange(self.bitcoin)
        # self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close - self.bitcoin_atr,
        #                                                      period=self.params.period_sma_bitcoin)

        # for d in self.datas:
        #     ticker = d._name
        #     self.inds[ticker] = {}
        #     self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high,
        #                                                               plot=False, subplot=False)
        #     self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low,
        #                                                             plot=False, subplot=False)
        #     self.inds[ticker]["average_true_range"] = bt.indicators.AverageTrueRange(d)
        #     self.inds[ticker]["sma_veryfast"] = bt.ind.SimpleMovingAverage(d.close,
        #                                                                    period=self.params.period_sma_veryfast,
        #                                                                    plot=False)
        #     self.inds[ticker]["sma_fast"] = bt.ind.SimpleMovingAverage(d.close,
        #                                                                period=self.params.period_sma_fast, plot=False)
        #     self.inds[ticker]["sma_mid"] = bt.ind.SimpleMovingAverage(d.close,
        #                                                               period=self.params.period_sma_mid, plot=False)
        #     self.inds[ticker]["sma_slow"] = bt.ind.SimpleMovingAverage(d.close,
        #                                                                period=self.params.period_sma_slow, plot=False)
        #     self.inds[ticker]["sma_veryslow"] = bt.ind.SimpleMovingAverage(d.close,
        #                                                                    period=self.params.period_sma_veryslow,
        #                                                                    plot=False)

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
    # def next(self):
    #     pos = len(self.data)
    #     if pos % self.params.modbuy == 0:
    #         # if abs(self.broker.getposition(self.datas[0]).size) < 0.01:
    #         self.long_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
    #         # self.stop_order = self.exec_trade(direction="sell", price=self.datas[0].close * 0.6, exectype=bt.Order.Stop)
    #         # print('self.stop_order after placing stop')
    #         # print(self.stop_order)
    #         # print('self.cancel_order after placing stop')
    #         # print(self.cancel_order)
    #
    #     if pos % self.params.modbuy != 0:
    #         # if self.broker.getposition(self.datas[0]).size > 0:
    #         self.short_order = self.exec_trade(direction="sell", exectype=self.params.exectype)
    #         # if self.stop_order:
    #         #     self.cancel_order = self.cancel(self.stop_order)
    #         #     print('self.stop_order after placing cancel')
    #         #     print(self.stop_order)
    #         #     print('self.cancel_order after placing cancel')
    #         #     print(self.cancel_order)

    def next(self):
        for i, d in enumerate(self.altcoins):
            ticker = d._name
            current_position = self.getposition(d).size
            # self.log('{} Position {}'.format(ticker, current_position))
            mod = len(self.data)
            # self.log(f'mod: {mod}')
            # volatility = self.inds[ticker]["average_true_range"][0] / d.close[0]
            volatility_factor = 1
            # volatility_factor = 1 / (volatility * 100)
            # if mod % self.params.modbuy == 0:
            if mod == 2:
                # self.orders[ticker] = [self.order_target_percent(data=d, target=(self.p.order_target_percent / 100) * volatility_factor)]
                # order_info = self.orders[ticker][0].ccxt_order['info']
                # qty = order_info['executedQty']
                # price = order_info['avgPrice']
                # quote = order_info['cumQuote']
                # self.log(f'Buy {qty} {ticker} @ {price} for {quote} USDT')
                try:
                    self.orders[ticker] = [self.order_target_percent(data=d, target=((
                                                                                                 self.p.order_target_percent / 100) * volatility_factor) / 2,
                                                                     execType=bt.Order.Limit, price=0.5 * d.open)]
                    # self.orders[ticker].append(self.order_target_percent(data=d, target=((
                    #                                                                                  self.p.order_target_percent / 100) * volatility_factor) / 2,
                    #                                                      execType=bt.Order.Limit, price=0.3 * d.open))
                    self.orders[ticker].append(self.order_target_percent(data=d, target=((
                                                                                                     self.p.order_target_percent / 100) * volatility_factor) / 2,
                                                                         execType=bt.Order.Market))


                    if ENV == PRODUCTION and TRADING == "LIVE":
                        order_info = self.orders[ticker][0].ccxt_order['info']
                        qty = order_info['origQty']
                        price = order_info['price']
                        self.log(f'Enter Long {qty} {ticker[:-4]} @ {price}')
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))

            # elif mod % self.params.modbuy != 0:
            elif mod == 4:
                self.orders[ticker] = [
                    self.order_target_percent(data=d, target=-(self.p.order_target_percent / 100) * volatility_factor)]
                order_info = self.orders[ticker][0].ccxt_order['info']
                qty = order_info['executedQty']
                price = order_info['avgPrice']
                quote = order_info['cumQuote']
                self.log(f'Sell {qty} {ticker} @ {price} for {quote} USDT')
            # elif mod % self.params.sell == 0:
            # elif mod == 6 or pos == 10:
            #     self.orders[ticker] = [
            #         self.order_target_percent(data=d, target=0)]
            if current_position > 0:
                order = self.order_target_percent(data=d, target=0)
                self.orders[ticker].append(order)
                order_info = self.orders[ticker][1].ccxt_order['info']
                qty = order_info['executedQty']
                price = order_info['avgPrice']
                quote = order_info['cumQuote']
                self.log(f'Close Long {qty} {ticker} @ {price} for {quote} USDT')
            elif current_position < 0:
                order = self.order_target_percent(data=d, target=0)
                self.orders[ticker].append(order)
                order_info = self.orders[ticker][1].ccxt_order['info']
                qty = order_info['executedQty']
                price = order_info['avgPrice']
                quote = order_info['cumQuote']
                self.log(f'Close Short {qty} {ticker} @ {price} for {quote} USDT')
