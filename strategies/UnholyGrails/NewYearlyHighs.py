import backtrader as bt
import backtrader_addons as bta
import datetime
import sys
from strategies.base import StrategyBase
from config import DEVELOPMENT, BASE, QUOTE, ENV, PRODUCTION, DEBUG, TRADING


class NewYearlyHighs(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_rolling_high', 500),
        ('period_rolling_low', 500),
        ('period_sma_bitcoin', 100),
        ('period_sma_veryfast', 10),
        ('period_sma_fast', 20),
        ('period_sma_mid', 50),
        ('period_sma_slow', 200),
        ('period_sma_veryslow', 500),
        # ('period_highest_high_slow', 20),
        # ('period_highest_high_mid', 10),
        # ('period_highest_high_fast', 5),
        ('order_target_percent', 5)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.orders = dict()
        self.bitcoin_atr = bt.indicators.AverageTrueRange(self.bitcoin)
        self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close-self.bitcoin_atr,
                                                            period=self.params.period_sma_bitcoin)

        for d in self.datas:
            ticker = d._name
            self.inds[ticker] = {}
            self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high, plot=False, subplot=False)
            self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low, plot=False, subplot=False)
            self.inds[ticker]["average_true_range"] = bt.indicators.AverageTrueRange(d)
            self.inds[ticker]["sma_veryfast"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_veryfast, plot=False)
            self.inds[ticker]["sma_fast"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_fast, plot=False)
            self.inds[ticker]["sma_mid"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_mid, plot=False)
            self.inds[ticker]["sma_slow"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_slow, plot=False)
            self.inds[ticker]["sma_veryslow"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_veryslow, plot=False)

            self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=False)
            self.inds[ticker]["adx"] = bt.ind.ADX(d, plot=False)
            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)
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

    def next(self):
        if self.i % 5 == 0:
            self.rebalance_portfolio()
        self.i += 1
        # for i, d in enumerate(self.altcoins):
        #     self.log(f'Available data for {(d._name)[:-4]}: {len(d)}')
        available = list(filter(lambda d: len(d) > 500, self.altcoins))
        available.sort(reverse=True, key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]) * (self.inds[d._name]["roc"][0]))
        for i, d in enumerate(available):
            ticker = d._name
            # self.log(abs(self.inds[ticker]["roc"][0]))
            current_position = self.getposition(d).size
            # self.log('{} Position {}'.format(ticker, current_position))
            if current_position > 0:
                if (self.bitcoin.low[0] < self.bitcoin_sma[0]) or (d.low[0] < self.inds[ticker]['rolling_low'][0]):
                    try:
                        order = self.order_target_percent(data=d, target=0)
                        self.orders[ticker].append(order)
                        if ENV == PRODUCTION and TRADING == "LIVE":
                            order_info = self.orders[ticker][1].ccxt_order['info']
                            qty = order_info['executedQty']
                            price = order_info['avgPrice']
                            quote = order_info['cumQuote']
                            self.log(f'Exit Long {qty} {ticker[:-4]} @ {price} for {quote} USDT')
                        else:
                            self.log(f'Exit Long {ticker[:-4]} @ {d.close[0]}')
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
            elif current_position < 0:
                if (self.bitcoin.high[0] > self.bitcoin_sma[0]) or (d.high[0] > self.inds[ticker]['rolling_high'][0]):
                    try:
                        order = self.order_target_percent(data=d, target=0)
                        self.orders[ticker].append(order)
                        if ENV == PRODUCTION and TRADING == "LIVE":
                            order_info = self.orders[ticker][1].ccxt_order['info']
                            qty = order_info['executedQty']
                            price = order_info['avgPrice']
                            quote = order_info['cumQuote']
                            self.log(f'Exit Short {qty} {ticker[:-4]} @ {price} for {quote} USDT')
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
            if current_position == 0:
                volatility = self.inds[ticker]["average_true_range"][0]/d.close[0]
                volatility_factor = 1/(volatility*100)
                closes_above_sma = 0
                for lookback in [0, -1, -2, -3, -4]:
                    if d.close[lookback] > self.inds[ticker]['sma_veryslow'][lookback]:
                        closes_above_sma += 1
                if self.bitcoin.close[0] > self.bitcoin_sma[0] and closes_above_sma == 5:
                    if d.close[0] > self.inds[ticker]['sma_fast'][0]:
                        if d.high[0] > self.inds[ticker]['rolling_high'][0]:
                            try:
                                # Market entry at close price
                                # self.orders[ticker] = [self.order_target_percent(data=d, target=((self.p.order_target_percent/100) * volatility_factor))]

                                # Staggerred limit entry adjusted by ROC
                                self.orders[ticker] = [self.order_target_percent(data=d, target=((self.p.order_target_percent/100) * volatility_factor)/2, execType=bt.Order.Limit, price=d.close[0] * (1 - abs(self.inds[ticker]['roc'][0])))]
                                self.orders[ticker].append(self.order_target_percent(data=d, target=((self.p.order_target_percent/100) * volatility_factor)/2, execType=bt.Order.Limit, price=d.close[0] * (1 - 2*abs(self.inds[ticker]['roc'][0]))))

                                # SMA
                                # self.orders[ticker] = [self.order_target_percent(data=d, target=((self.p.order_target_percent/100) * volatility_factor)/2, execType=bt.Order.Limit, price=self.inds[ticker]['sma_fast'][0])]
                                # self.orders[ticker].append(self.order_target_percent(data=d, target=((self.p.order_target_percent/100) * volatility_factor)/2, execType=bt.Order.Limit, price=self.inds[ticker]['sma_mid'][0]))

                                # ATR
                                # self.orders[ticker] = [self.order_target_percent(data=d, target=((self.p.order_target_percent/100) * volatility_factor)/2, execType=bt.Order.Limit, price=d.close[0] - (self.inds[ticker]['average_true_range'][0])/4)]
                                # self.orders[ticker].append(self.order_target_percent(data=d, target=((self.p.order_target_percent/100) * volatility_factor)/2, execType=bt.Order.Limit, price=d.close[0] - (self.inds[ticker]['average_true_range'][0])/2))


                                if ENV == PRODUCTION and TRADING == "LIVE":
                                    order_info = self.orders[ticker][0].ccxt_order['info']
                                    qty = order_info['origQty']
                                    price = order_info['price']
                                    self.log(f'Enter Long {qty} {ticker[:-4]} @ {price}')
                            except Exception as e:
                                self.log("ERROR: {}".format(sys.exc_info()[0]))
                                self.log("{}".format(e))

                elif self.bitcoin.close[0] < self.bitcoin_sma[0]:
                    if d.low[0] < self.inds[ticker]['rolling_low'][0]:
                        if self.inds[ticker]['sma_veryfast'][0] < self.inds[ticker]['sma_mid'][0] and self.inds[ticker]['sma_slow'][0] < self.inds[ticker]['sma_veryslow'][0]:
                            try:
                                self.orders[ticker] = [self.order_target_percent(data=d, target=-(self.p.order_target_percent/100) * volatility_factor)]
                                if ENV == PRODUCTION and TRADING == "LIVE":
                                    order_info = self.orders[ticker][0].ccxt_order['info']
                                    qty = order_info['executedQty']
                                    price = order_info['avgPrice']
                                    quote = order_info['cumQuote']
                                    self.log(f'Enter Short {qty} {ticker[:-4]} @ {price} for {quote} USDT')
                                else:
                                    self.log(f'Enter Short {ticker[:-4]} @ {d.close[0]}')
                            except Exception as e:
                                self.log("ERROR: {}".format(sys.exc_info()[0]))
                                self.log("{}".format(e))
            #  Original
            # if current_position == 0:
            #     if self.bitcoin.close[0] > self.bitcoin_sma[0]:
            #         if d.high[0] > self.inds[ticker]['rolling_high'][-10]:
            #             self.orders[ticker] = [self.order_target_percent(data=d, target=0.2)]
            #             self.log('{} Buy initiated {}'.format(ticker, self.orders[ticker][0]))

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

    def rebalance_portfolio(self):
        # self.log('Rebalancing Portfolio...')
        # only look at data that we can have indicators for
        self.rankings = list(filter(lambda d: len(d) > 500, self.altcoins))
        self.rankings.sort(key=lambda d: (self.inds[d._name]["rsi"][0])*(self.inds[d._name]["adx"][0]))

        # Rebalance any coins in lowest momentum that are in positions
        for i, d in enumerate(self.rankings[:5]):
            if self.getposition(d).size:
                try:
                    order = self.order_target_percent(data=d, target=abs(self.inds[d._name]["roc"][0]), execType=bt.Order.Limit)
                    ticker = d._name
                    self.orders[ticker].append(order)
                    self.log(f'Rebalancing {ticker[:-4]} @ {d.close[0]}')
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))
        # if self.spy < self.spy_sma200:
        #     return

        # buy altcoins with remaining cash
        # for i, d in enumerate(self.rankings[:int(num_altcoins * 0.2)]):
        #     cash = self.broker.get_cash()
        #     value = self.broker.get_value()
        #     if cash <= 0:
        #         break
        #     if not self.getposition(self.data).size:
        #         size = value * 0.001 / self.inds[d]["atr20"]
        #         self.buy(d, size=size)
