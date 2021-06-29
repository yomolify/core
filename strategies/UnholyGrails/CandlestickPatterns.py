import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT
import datetime as dt
from indicators.SuperTrend import SuperTrend
from indicators.VWAP import VWAP

class CandlestickPatterns(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_rolling_high', 500),
        ('period_rolling_low', 500),
        ('period_sma_bitcoin', 250),
        ('period_sma_veryfast', 10),
        ('period_vol_sma', 50),
        ('period_sma_fast', 20),
        ('period_sma_mid', 50),
        ('period_sma_midslow', 100),
        ('period_sma_slow', 200),
        ('period_sma_veryslow', 500),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        ('order_target_percent', 5)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.strategy = "CandleStickPatterns"
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.pos = {}
        self.just_sold = {}
        self.blocked_for = {}
        self.stop_order = dict()
        self.orders = dict()
        self.entry_bar_height = {}
        self.entry_type = {}
        self.stop_order = {}
        self.tp_orders = {}
        self.blocked_tickers = []
        self.delayed_tickers = []

        self.bitcoin_atr = bt.indicators.AverageTrueRange(self.bitcoin, plot=False)
        self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close-self.bitcoin_atr,
                                                            period=self.params.period_sma_bitcoin, plot=False)
        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            self.entry_bar_height[ticker] = None
            self.entry_type[ticker] = None
            self.stop_order[ticker] = None
            self.tp_orders[ticker] = []
            self.pos[ticker] = {}
            self.just_sold[ticker] = False
            self.blocked_for[ticker] = 0
            self.inds[ticker] = {}
            self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high, plot=False, subplot=False)
            self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low, plot=False, subplot=False)
            self.inds[ticker]["atr"] = bt.indicators.AverageTrueRange(d, plot=False)
            self.inds[ticker]["VWAP"] = VWAP(d, period=288, plot=True)
            self.inds[ticker]["sma_veryfast"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_veryfast, plot=False)
            self.inds[ticker]["sma_fast"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_fast, plot=False)
            self.inds[ticker]["sma_mid"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_mid, plot=True)
            self.inds[ticker]["sma_midslow"] = bt.ind.SimpleMovingAverage(d.close,
                                                                      period=self.params.period_sma_midslow, plot=True)
            self.inds[ticker]["sma_slow"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_slow, plot=True)
            self.inds[ticker]["sma_veryslow"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_veryslow, plot=True)
            self.inds[ticker]["sma_highs"] = bt.ind.SimpleMovingAverage(d.high,
                period=self.params.period_sma_highs, plot=False)
            self.inds[ticker]["sma_lows"] = bt.ind.SimpleMovingAverage(d.low,
                period=self.params.period_sma_lows, plot=False)
            self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=True)
            self.inds[ticker]["adx"] = bt.ind.ADX(d, plot=True)
            self.inds[ticker]["adx_20"] = bt.ind.ADX(d, period=20, plot=False)
            self.inds[ticker]["sma_adx_20"] = bt.ind.HMA(self.inds[ticker]["adx_20"], period=20, plot=False, subplot=False)
            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)
            self.inds[ticker]["sma_roc"] = bt.ind.HMA(self.inds[ticker]["roc"], plot=False)
            self.inds[ticker]["super_trend"] = SuperTrend(d, plot=False, subplot=False)
            self.inds[ticker]["vol_sma"] = bt.ind.HullMovingAverage(d.volume,
                                                                    period=self.params.period_vol_sma,
                                                                    plot=False, subplot=False)


    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            available = list(filter(lambda d: len(d) > 500, self.altcoins))
            available.sort(reverse=True, key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]) * (self.inds[d._name]["roc"][0]))
            self.blocked_tickers = []
            for i, d in enumerate(available):
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
                    # if self.pos[ticker]["profit_percentage"] > 205:
                    #     self.pos[ticker]["new_sl_price"] = 2.9 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 195:
                    # #     self.pos[ticker]["new_sl_price"] = 2.8 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 185:
                    #     self.pos[ticker]["new_sl_price"] = 2.7 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 175:
                    # #     self.pos[ticker]["new_sl_price"] = 2.6 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 165:
                    #     self.pos[ticker]["new_sl_price"] = 2.5 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 155:
                    # #     self.pos[ticker]["new_sl_price"] = 2.4 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 145:
                    #     self.pos[ticker]["new_sl_price"] = 2.3 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 135:
                    # #     self.pos[ticker]["new_sl_price"] = 2.2 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 125:
                    #     self.pos[ticker]["new_sl_price"] = 2.1 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 115:
                    # #     self.pos[ticker]["new_sl_price"] = 2 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 105:
                    #     self.pos[ticker]["new_sl_price"] = 1.9 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 95:
                    # #     self.pos[ticker]["new_sl_price"] = 1.8 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 85:
                    #     self.pos[ticker]["new_sl_price"] = 1.7 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 75:
                    # #     self.pos[ticker]["new_sl_price"] = 1.6 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 65:
                    #     self.pos[ticker]["new_sl_price"] = 1.5 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 55:
                    # #     self.pos[ticker]["new_sl_price"] = 1.4 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 45:
                    #     self.pos[ticker]["new_sl_price"] = 1.3 * self.pos[ticker]["price"]
                    # # elif self.pos[ticker]["profit_percentage"] > 35:
                    # #     self.pos[ticker]["new_sl_price"] = 1.2 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 25:
                    #     self.pos[ticker]["new_sl_price"] = 1.1 * self.pos[ticker]["price"]
                    if self.pos[ticker]["profit_percentage"] > 1:
                        self.pos[ticker]["new_sl_price"] = d.low[0] - 1.1*self.inds[ticker]["atr"][0]
                    # elif self.pos[ticker]["profit_percentage"] > 15:
                    #     self.pos[ticker]["new_sl_price"] = 1 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] < 5:
                    # self.log(f'{ticker} Long profit > 15%, updating stop win to 10%')
                    # self.pos[ticker]["new_sl_price"] = self.pos[ticker]["sl_price"]
                    # elif self.pos[ticker]["profit_percentage"] < 5:
                    #     if self.pos[ticker]["new_sl_price"] is None:
                    #         # self.stop_order[ticker] = self.close(data=d, price=0.8*d.close[0],
                    #         #                                      exectype=bt.Order.StopTrail,
                    #         #                                      trailamount=d.close[0] / 10)
                    #         self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["sl_price"],
                    #                                              exectype=bt.Order.Stop
                    #                                              )
                    #         self.pos[ticker]["new_sl_price"] = self.pos[ticker]["sl_price"]
                    # if self.pos[ticker]["reset_stop"] is True or self.pos[ticker]["new_sl_price"] and self.pos[ticker]["sl_price"] and self.pos[ticker]["new_sl_price"] > self.pos[ticker]["sl_price"]:
                    #     self.log(
                    #         f'{ticker} Update stop from {self.pos[ticker]["sl_price"]} to {self.pos[ticker]["new_sl_price"]}')
                    #     self.pos[ticker]["sl_price"] = self.pos[ticker]["new_sl_price"]
                    #     if ticker in self.stop_order:
                    #         self.cancel(self.stop_order[ticker])
                    #     self.stop_order[ticker] = None
                    #     self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)
                    #     self.pos[ticker]["reset_stop"] = False
                        # self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.StopTrail, trailpercent=0.1)
                        # self.stop_order[ticker] = self.sell(data=d, size=current_position/2, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)

                if current_position > 0:
                    if self.entry_type[ticker] == "LongHammer":
                        if self.tp_orders[ticker]:
                            for tp_order in self.tp_orders[ticker]:
                                self.cancel(tp_order)
                            self.tp_orders[ticker] = []
                        else:
                            self.tp_orders[ticker].append(self.close(data=d, price=self.inds[ticker]["sma_mid"][0], exectype=bt.Order.Limit))
                        # if d.close[0] < self.inds[ticker]["super_trend"][0]:
                        #     try:
                        #         order = self.add_order(data=d, target=0, type='market')
                        #         self.log(f'Trend fin, closing long {ticker}')
                        #     except Exception as e:
                        #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                        #         self.log("{}".format(e))
                        # When away from vwap and consolidating, enter with tp at vwap
                elif current_position < 0:
                    if self.entry_type[ticker] == "ShortBearishEngulfing":
                        if len(self.tp_orders[ticker]) == 0:
                            self.tp_orders[ticker].append(self.buy(data=d, size=self.pos[ticker]["size"]/3, price=self.inds[ticker]["sma_veryslow"][0], exectype=bt.Order.Limit))
                            self.tp_orders[ticker].append(self.buy(data=d, size=self.pos[ticker]["size"]/3, price=self.inds[ticker]["sma_veryslow"][0] - 0.5*self.inds[ticker]["atr"][0], exectype=bt.Order.Limit))
                            self.tp_orders[ticker].append(self.buy(data=d, size=self.pos[ticker]["size"]/3, price=self.inds[ticker]["sma_veryslow"][0] - 1*self.inds[ticker]["atr"][0], exectype=bt.Order.Limit))
                        elif len(self.tp_orders[ticker]) <= 3:
                            for tp_order in self.tp_orders[ticker]:
                                if tp_order.status == 4:
                                    self.tp_orders[ticker].remove(tp_order)
                                    # Move stop to rolling high
                                    if self.stop_order[ticker]:
                                        self.cancel(self.stop_order[ticker])
                                    self.log((self.pos[ticker]["price"]+d.close[0])/2)
                                    self.stop_order[ticker] = self.close(data=d, price=(self.pos[ticker]["price"]+d.close[0])/2, exectype=bt.Order.Stop)
                                    continue

                                # else:
                                #     self.cancel(tp_order)
                                #     self.tp_orders[ticker].remove(tp_order)
                        self.log(len(self.tp_orders[ticker]))
                    # if d.close[0] > self.inds[ticker]["super_trend"][0]:
                    #     try:
                    #         order = self.add_order(data=d, target=0, type='market')
                    #         self.blocked_tickers.append(ticker)
                    #         self.log(f'Trend fin, closing short {ticker}')
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
                if current_position == 0:
                    self.cancel(self.stop_order[ticker])
                    if self.tp_orders[ticker]:
                        for tp_order in self.tp_orders[ticker]:
                            self.cancel(tp_order)
                        self.tp_orders[ticker] = []
                    # Bullish Hammer at the end of a downtrend
                    if 2*(d.open[0] - d.close[0]) < d.high[0] - d.low[0] and d.high[0] - d.open[0] < 0.1*(d.open[0] - d.close[0]) and self.inds[ticker]["rsi"][0] < 40:
                        self.entry_type[ticker] = "LongHammer"
                        try:
                            self.orders[ticker] = [self.add_order(data=d, target=0.99, type="market")]
                            self.pos[ticker]["sl_price"] = d.close[0] - self.inds[ticker]["atr"][0]
                            self.pos[ticker]["new_sl_price"] = None
                            self.pos[ticker]["profit_percentage"] = 0
                            self.pos[ticker]["reset_stop"] = False
                            self.log(f'LongHammer {ticker}')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                    # d.volume[0] > self.inds[ticker]['vol_sma'][0] and d.close[0] > self.inds[ticker]['sma_slow'][0] - 2 * self.inds[ticker]["atr"][0] and self.inds[ticker]['rsi'][0] < 80
                    elif d.close[0] < d.open[0] and self.inds[ticker]["rsi"][-1] > 60:
                        self.entry_type[ticker] = "ShortBearishEngulfing"
                        try:
                            self.orders[ticker] = [self.add_order(data=d, target=-0.99, type="market")]
                            # self.pos[ticker]["sl_price"] = d.close[0] + self.inds[ticker]["atr"][0]
                            self.pos[ticker]["new_sl_price"] = None
                            self.pos[ticker]["profit_percentage"] = 0
                            self.pos[ticker]["reset_stop"] = False
                            self.log(f'ShortBearishEngulfing {ticker}')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
            if len(self.to_place_orders) > 0:
                order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                for order_chunk in order_chunks:
                    self.place_batch_order(order_chunk)
