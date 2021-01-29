import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT


class GCSImproved(StrategyBase):
    # 68 and 40 without stops
    # 286 and 39 with HullMA
    params = (
        ('exectype', bt.Order.Market),
        ('period_rolling_high', 500),
        ('period_rolling_low', 500),
        ('period_sma_bitcoin', 250),
        ('period_sma_veryfast', 10),
        ('period_sma_fast', 20),
        ('period_sma_mid', 50),
        ('period_sma_slow', 200),
        ('period_sma_veryslow', 500),
        ('period_vol_sma', 50),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        # ('order_target_percent', 100)
        ('order_target_percent', 99),
        ('period_highest_high_slow', 20),
        ('period_highest_high_mid', 10),
        ('period_highest_high_fast', 5),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.pos = {}
        self.orders = dict()
        self.stop_order = dict()
        self.bitcoin_atr = bt.indicators.AverageTrueRange(self.bitcoin, plot=False)
        self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close - self.bitcoin_atr,
                                                             period=self.params.period_sma_bitcoin, plot=False)
        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            self.pos[ticker] = {}
            self.inds[ticker] = {}
            self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high,
                                                                      plot=False, subplot=False)
            self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low,
                                                                    plot=False, subplot=False)
            self.inds[ticker]["average_true_range"] = bt.indicators.AverageTrueRange(d)
            self.inds[ticker]["sma_veryfast"] = bt.ind.HullMovingAverage(d.close,
                                                                           period=self.params.period_sma_veryfast,
                                                                           plot=False)
            self.inds[ticker]["sma_fast"] = bt.ind.HullMovingAverage(d.close,
                                                                       period=self.params.period_sma_fast, plot=True)
            self.inds[ticker]["sma_mid"] = bt.ind.HullMovingAverage(d.close,
                                                                      period=self.params.period_sma_mid, plot=True)
            self.inds[ticker]["sma_slow"] = bt.ind.HullMovingAverage(d.close,
                                                                       period=self.params.period_sma_slow, plot=True)
            # self.inds[ticker]["sma_veryslow"] = bt.ind.HullMovingAverage(d.close,
            #                                                                period=self.params.period_sma_veryslow,
            #                                                                plot=True)
            self.inds[ticker]["vol_sma"] = bt.ind.HullMovingAverage(d.volume,
                                                                         period=self.params.period_vol_sma,
                                                                         plot=True, subplot=True)

            self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=False)
            self.inds[ticker]["adx"] = bt.ind.ADX(d, plot=False)
            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)
            self.inds[ticker]["sma_roc"] = bt.ind.HMA(self.inds[ticker]["roc"], period=self.params.period_vol_sma, plot=False)
            self.highest_high_slow = bt.ind.Highest(
                period=self.params.period_highest_high_slow, plot=False)
            self.highest_high_mid = bt.ind.Highest(
                period=self.params.period_highest_high_mid, plot=False)
            self.highest_high_fast = bt.ind.Highest(
                period=self.params.period_highest_high_fast, plot=False)
    def updateStops(self, d):
        ticker = d._name
        current_position = self.get_position(d=d, attribute='size')
        self.pos[ticker]["size"] = self.get_position(d=d, attribute='size')
        self.pos[ticker]["price"] = self.get_position(d=d, attribute='price')
        if current_position > 0:
            # StopWin
            self.pos[ticker]["previous_profit_percentage"] = self.pos[ticker]["profit_percentage"]
            self.pos[ticker]["profit"] = d.close[0] - self.pos[ticker]["price"]
            self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker][
                "price"]) * 100
            if self.pos[ticker]["profit_percentage"] > 205:
                self.pos[ticker]["new_sl_price"] = 2.9 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 195:
            #     self.pos[ticker]["new_sl_price"] = 2.8 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 185:
                self.pos[ticker]["new_sl_price"] = 2.7 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 175:
            #     self.pos[ticker]["new_sl_price"] = 2.6 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 165:
                self.pos[ticker]["new_sl_price"] = 2.5 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 155:
            #     self.pos[ticker]["new_sl_price"] = 2.4 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 145:
                self.pos[ticker]["new_sl_price"] = 2.3 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 135:
            #     self.pos[ticker]["new_sl_price"] = 2.2 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 125:
                self.pos[ticker]["new_sl_price"] = 2.1 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 115:
            #     self.pos[ticker]["new_sl_price"] = 2 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 105:
                self.pos[ticker]["new_sl_price"] = 1.9 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 95:
            #     self.pos[ticker]["new_sl_price"] = 1.8 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 85:
                self.pos[ticker]["new_sl_price"] = 1.7 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 75:
            #     self.pos[ticker]["new_sl_price"] = 1.6 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 65:
                self.pos[ticker]["new_sl_price"] = 1.5 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 55:
            #     self.pos[ticker]["new_sl_price"] = 1.4 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 45:
                self.pos[ticker]["new_sl_price"] = 1.3 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 35:
            #     self.pos[ticker]["new_sl_price"] = 1.2 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 25:
                self.pos[ticker]["new_sl_price"] = 1.1 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] > 15:
                self.pos[ticker]["new_sl_price"] = 1 * self.pos[ticker]["price"]
            elif self.pos[ticker]["profit_percentage"] < 5:
                self.log(f'{ticker} Long profit > 15%, updating stop win to 10%')
                self.pos[ticker]["new_sl_price"] = self.pos[ticker]["sl_price"]
            # elif self.pos[ticker]["profit_percentage"] < 5:
            #     if self.pos[ticker]["new_sl_price"] is None:
            #         # self.stop_order[ticker] = self.close(data=d, price=0.8*d.close[0],
            #         #                                      exectype=bt.Order.StopTrail,
            #         #                                      trailamount=d.close[0] / 10)
            #         self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["sl_price"],
            #                                              exectype=bt.Order.Stop
            #                                              )
            #         self.pos[ticker]["new_sl_price"] = self.pos[ticker]["sl_price"]
            if self.pos[ticker]["reset_stop"] is True or self.pos[ticker]["new_sl_price"] and self.pos[ticker][
                "sl_price"] and self.pos[ticker]["new_sl_price"] > self.pos[ticker]["sl_price"]:
                self.log(
                    f'{ticker} Update stop from {self.pos[ticker]["sl_price"]} to {self.pos[ticker]["new_sl_price"]}')
                self.pos[ticker]["sl_price"] = self.pos[ticker]["new_sl_price"]
                if ticker in self.stop_order:
                    self.cancel(self.stop_order[ticker])
                self.stop_order[ticker] = None
                self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"],
                                                     exectype=bt.Order.Stop)
                self.pos[ticker]["reset_stop"] = False
                # self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.StopTrail, trailpercent=0.05)
                # self.stop_order[ticker] = self.sell(data=d, size=current_position/2, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)

            elif d.close[0] < self.inds[ticker]['rolling_low'][-1]:
                try:
                    order = self.add_order(data=d, target=0, type='market')
                    if ticker in self.stop_order:
                        self.cancel(self.stop_order[ticker])
                    self.log('Long Sell Signal')
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))
            elif self.pos[ticker]["profit_percentage"] > 100:
                try:
                    order = self.sell(data=d, size=self.pos[ticker]["size"], type='market')
                    if ticker in self.stop_order:
                        self.cancel(self.stop_order[ticker])
                    self.log(f'Reduce 100% {ticker} in 100% profit')
                    self.pos[ticker]["reset_stop"] = True
                    # self.pos[ticker]["new_sl_price"] = 1.05*self.pos[ticker]["sl_price"]
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))
            elif self.pos[ticker]["profit_percentage"] > 75:
                try:
                    order = self.sell(data=d, size=self.pos[ticker]["size"] / 1.5, type='market')
                    if ticker in self.stop_order:
                        self.cancel(self.stop_order[ticker])
                    self.log(f'Reduce 67% {ticker} in 75% profit')
                    self.pos[ticker]["reset_stop"] = True
                    # self.pos[ticker]["new_sl_price"] = 1.05*self.pos[ticker]["sl_price"]
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))
            elif self.pos[ticker]["profit_percentage"] > 50:
                try:
                    order = self.sell(data=d, size=self.pos[ticker]["size"] / 2, type='market')
                    if ticker in self.stop_order:
                        self.cancel(self.stop_order[ticker])
                    self.log(f'Reduce 50% {ticker} in 50% profit')
                    self.pos[ticker]["reset_stop"] = True
                    # self.pos[ticker]["new_sl_price"] = 1.05*self.pos[ticker]["sl_price"]
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))
            elif self.pos[ticker]["profit_percentage"] > 5 and self.pos[ticker]["previous_profit_percentage"] > 0 and (
                    (self.pos[ticker]["profit_percentage"] - self.pos[ticker]["previous_profit_percentage"]) /
                    self.pos[ticker]["previous_profit_percentage"]) > 0.05:
                if self.pos[ticker]["profit_percentage"] > 40:
                    try:
                        order = self.sell(data=d, size=self.pos[ticker]["size"] / 2, type='market')
                        if ticker in self.stop_order:
                            self.cancel(self.stop_order[ticker])
                        self.log(f'Reduce 50% {ticker} in 40% profit')
                        self.pos[ticker]["reset_stop"] = True
                        # self.pos[ticker]["new_sl_price"] = 1.05*self.pos[ticker]["sl_price"]
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                elif self.pos[ticker]["profit_percentage"] > 30:
                    try:
                        order = self.sell(data=d, size=self.pos[ticker]["size"] / 3, type='market')
                        if ticker in self.stop_order:
                            self.cancel(self.stop_order[ticker])
                        self.log(f'Reduce 33% {ticker} in 25% profit')
                        self.pos[ticker]["reset_stop"] = True
                        # self.pos[ticker]["new_sl_price"] = 1.05*self.pos[ticker]["sl_price"]
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                elif self.pos[ticker]["profit_percentage"] > 20:
                    try:
                        order = self.sell(data=d, size=self.pos[ticker]["size"] / 4, type='market')
                        if ticker in self.stop_order:
                            self.cancel(self.stop_order[ticker])
                        self.log(f'Reduce 25% {ticker} in 20% profit')
                        self.pos[ticker]["reset_stop"] = True
                        # self.pos[ticker]["new_sl_price"] = 1.05*self.pos[ticker]["sl_price"]
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                elif self.pos[ticker]["profit_percentage"] > 15:
                    try:
                        order = self.sell(data=d, size=self.pos[ticker]["size"] / 5, type='market')
                        if ticker in self.stop_order:
                            self.cancel(self.stop_order[ticker])
                        self.log(f'Reduce 20% {ticker} in 15% profit')
                        self.pos[ticker]["reset_stop"] = True
                        # self.pos[ticker]["new_sl_price"] = 1.025*self.pos[ticker]["sl_price"]
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                elif self.pos[ticker]["profit_percentage"] > 10:
                    try:
                        order = self.sell(data=d, size=self.pos[ticker]["size"] / 6, type='market')
                        if ticker in self.stop_order:
                            self.cancel(self.stop_order[ticker])
                        self.log(f'Reduce 16% {ticker} in 10% profit')
                        self.pos[ticker]["reset_stop"] = True
                        # self.pos[ticker]["new_sl_price"] = 1.025*self.pos[ticker]["sl_price"]
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                else:
                    try:
                        order = self.sell(data=d, size=self.pos[ticker]["size"] / 8, type='market')
                        if ticker in self.stop_order:
                            self.cancel(self.stop_order[ticker])
                        self.log(f'Reduce 20% {ticker} in 5% profit')
                        self.pos[ticker]["reset_stop"] = True
                        # self.pos[ticker]["new_sl_price"] = 1.01*self.pos[ticker]["sl_price"]
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
        elif current_position < 0:
            self.pos[ticker]["profit"] = self.pos[ticker]["price"] - d.close[0]
            self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker][
                "price"]) * 100
            if self.pos[ticker]["profit_percentage"] > 65:
                self.pos[ticker]["new_sl_price"] = 1.5 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 55:
            #     self.pos[ticker]["new_sl_price"] = 1.4 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 45:
            #     self.pos[ticker]["new_sl_price"] = 0.85 * self.pos[ticker]["price"]
            # elif self.pos[ticker]["profit_percentage"] > 35:
            #     self.pos[ticker]["new_sl_price"] = 1.2 * self.pos[ticker]["price"]
            if self.pos[ticker]["profit_percentage"] > 10:
                self.pos[ticker]["new_sl_price"] = self.highest_high_mid[0]
            elif self.pos[ticker]["profit_percentage"] > 5:
                self.pos[ticker]["new_sl_price"] = self.highest_high_fast[0]
            # Initial stop
            # elif self.pos[ticker]["profit_percentage"] < 15:
            # self.log(f'sl = {self.pos[ticker]["sl_price"]}')
            # self.log(f'new sl = {self.pos[ticker]["new_sl_price"]}')
            # Initial stop
            # if self.pos[ticker]["new_sl_price"] is None:
            # self.stop_order[ticker] = self.close(data=d, price=0.8*d.close[0],
            #                                      exectype=bt.Order.StopTrail,
            #                                      trailamount=d.close[0] / 10)
            # self.stop_order[ticker] = self.close(data=d, price=0.8*d.close[0],
            #                                      exectype=bt.Order.Stop
            #                                      )
            # self.pos[ticker]["new_sl_price"] = self.pos[ticker]["sl_price"]
            if self.pos[ticker]["new_sl_price"] and self.pos[ticker]["sl_price"] and \
                    self.pos[ticker][
                        "new_sl_price"] < self.pos[ticker]["sl_price"]:
                self.log(
                    f'{ticker} Update short stop from {self.pos[ticker]["sl_price"]} to {self.pos[ticker]["new_sl_price"]}')
                self.pos[ticker]["sl_price"] = self.pos[ticker]["new_sl_price"]
                if ticker in self.stop_order:
                    self.cancel(self.stop_order[ticker])
                self.stop_order[ticker] = None
                # self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)
                self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"],
                                                     exectype=bt.Order.StopTrail, trailpercent=0.1)
            if d.close[0] > self.inds[ticker]['rolling_high'][-1] + self.inds[ticker]["average_true_range"][0]:
                try:
                    order = self.add_order(data=d, target=0, type="market")
                    print("Short close signal")
                    if ticker in self.stop_order:
                        self.cancel(self.stop_order[ticker])
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))
    # def enter_long(self, d):
    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            # Without rebalance = 217 & 40
            # With 218 and 41
            # if self.i % 20 == 0:
            #     self.rebalance_portfolio()
            # self.i += 1
            available = list(filter(lambda d: len(d) > 500, self.altcoins))
            available.sort(reverse=True,
                           key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]) * (
                           self.inds[d._name]["roc"][0]))
            for i, d in enumerate(available):
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                # self.updateStops(d)
                if current_position > 0:
                    if self.inds[ticker]['sma_veryfast'][0] > self.inds[ticker]['sma_fast'][0] > self.inds[ticker]['sma_mid'][0]:
                        # self.enter_long()
                        try:
                            self.add_order(data=d, target=(
                                        (self.p.order_target_percent / 100) * volatility_factor),
                                                                  type="market")
                            self.pos[ticker]["sl_price"] = d.close[0] - self.inds[ticker]["average_true_range"][0]
                            self.pos[ticker]["new_sl_price"] = None
                            self.pos[ticker]["profit_percentage"] = 0
                            self.pos[ticker]["reset_stop"] = False
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                current_position = self.get_position(d=d, attribute='size')
                if current_position == 0:
                    volatility = self.inds[ticker]["average_true_range"][0] / d.close[0]
                    volatility_factor = 1 / (volatility * 100)
                    # TODO - if percentage gain in the last 5 candles is > 10 don't enter
                    # if d.volume[0] > self.inds[ticker]['vol_sma'][0] and d.close[0] > self.inds[ticker]['sma_slow'][0] - 2*self.inds[ticker]["average_true_range"][0] and self.inds[ticker]['rsi'][0] < 80 or self.inds[ticker]['rsi'][0] < 20:
                    if self.inds[ticker]['sma_veryfast'][0] > self.inds[ticker]['sma_fast'][0] > self.inds[ticker]['sma_mid'][0]:
                        try:
                            self.add_order(data=d, target=(
                                        (self.p.order_target_percent / 100) * volatility_factor),
                                                                  type="market")
                            self.pos[ticker]["sl_price"] = d.close[0] - self.inds[ticker]["average_true_range"][0]
                            self.pos[ticker]["new_sl_price"] = None
                            self.pos[ticker]["profit_percentage"] = 0
                            self.pos[ticker]["reset_stop"] = False
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                    # elif self.inds[ticker]['rsi'][0] > 85:
                    #     try:
                    #         self.orders[ticker] = [self.add_order(data=d, target=-(self.p.order_target_percent/100) * volatility_factor, type="market")]
                    #         self.pos[ticker]["sl_price"] = d.close[0] + self.inds[ticker]["average_true_range"][0]
                    #         self.pos[ticker]["new_sl_price"] = None
                    #         self.pos[ticker]["profit_percentage"] = 0
                    #         self.pos[ticker]["reset_stop"] = False
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
            if len(self.to_place_orders) > 0:
                order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                for order_chunk in order_chunks:
                    self.place_batch_order(order_chunk)
