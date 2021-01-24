import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT


class NewYearlyHighsStops(StrategyBase):
    # 68 and 40 without stops
    # 250 and 50 without stops
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
        ('period_sma_veryslow', 500),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        ('order_target_percent', 5)
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
        self.bitcoin_atr = bt.indicators.AverageTrueRange(self.bitcoin)
        self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close - self.bitcoin_atr,
                                                             period=self.params.period_sma_bitcoin)
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
            self.inds[ticker]["sma_veryfast"] = bt.ind.SimpleMovingAverage(d.close,
                                                                           period=self.params.period_sma_veryfast,
                                                                           plot=False)
            self.inds[ticker]["sma_fast"] = bt.ind.SimpleMovingAverage(d.close,
                                                                       period=self.params.period_sma_fast, plot=False)
            self.inds[ticker]["sma_mid"] = bt.ind.SimpleMovingAverage(d.close,
                                                                      period=self.params.period_sma_mid, plot=False)
            self.inds[ticker]["sma_slow"] = bt.ind.SimpleMovingAverage(d.close,
                                                                       period=self.params.period_sma_slow, plot=False)
            self.inds[ticker]["sma_veryslow"] = bt.ind.SimpleMovingAverage(d.close,
                                                                           period=self.params.period_sma_veryslow,
                                                                           plot=False)
            self.inds[ticker]["sma_highs"] = bt.ind.SimpleMovingAverage(d.high,
                                                                        period=self.params.period_sma_highs, plot=False)
            self.inds[ticker]["sma_lows"] = bt.ind.SimpleMovingAverage(d.low,
                                                                       period=self.params.period_sma_lows, plot=False)
            self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=False)
            self.inds[ticker]["adx"] = bt.ind.ADX(d, plot=False)
            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)

    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            if self.i % 20 == 0:
                self.rebalance_portfolio()
            self.i += 1
            available = list(filter(lambda d: len(d) > 500, self.altcoins))
            available.sort(reverse=True,
                           key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]) * (
                           self.inds[d._name]["roc"][0]))
            for i, d in enumerate(available):
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                self.pos[ticker]["size"] = self.get_position(d=d, attribute='size')
                self.pos[ticker]["price"] = self.get_position(d=d, attribute='price')
                if current_position > 0:
                    # StopWin
                    self.pos[ticker]["profit"] = d.close[0] - self.pos[ticker]["price"]
                    self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker][
                        "price"]) * 100
                    # if self.pos[ticker]["profit_percentage"] > 95:
                    #     # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                    #     self.pos[ticker]["new_sl_price"] = 1.8 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 85:
                        # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                    #     self.pos[ticker]["new_sl_price"] = 1.7 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 75:
                    #     # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                    #     self.pos[ticker]["new_sl_price"] = 1.6 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 65:
                    #     # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                    #     self.pos[ticker]["new_sl_price"] = 1.5 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 55:
                    #     # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                    #     self.pos[ticker]["new_sl_price"] = 1.4 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 45:
                    #     # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                    #     self.pos[ticker]["new_sl_price"] = 1.3 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 35:
                    #     # self.log(f'{ticker} Long profit > 35%, updating stop win to 30%')
                    #     self.pos[ticker]["new_sl_price"] = 1.2 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 25:
                    #     # self.log(f'{ticker} Long profit > 25%, updating stop win to 20%')
                    #     self.pos[ticker]["new_sl_price"] = 1.1 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 15:
                    #     # self.log(f'{ticker} Long profit > 15%, updating stop win to 10%')
                    #     self.pos[ticker]["new_sl_price"] = 1 * self.pos[ticker]["price"]
                    # elif self.pos[ticker]["profit_percentage"] > 5:
                    #     self.log(f'{ticker} Long profit > 5%, updating stop win to 0%')
                    #     self.pos[ticker]["new_sl_price"] = 0.95 * self.pos[ticker]["price"]
                    if self.pos[ticker]["new_sl_price"] and self.pos[ticker]["sl_price"] and self.pos[ticker]["new_sl_price"] > self.pos[ticker]["sl_price"]:
                        self.log(
                            f'{ticker} Update stop from {self.pos[ticker]["sl_price"]} to {self.pos[ticker]["new_sl_price"]}')
                        self.pos[ticker]["sl_price"] = self.pos[ticker]["new_sl_price"]
                        self.cancel(self.stop_order[ticker])
                        self.stop_order[ticker] = None
                        self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["new_sl_price"], exectype=bt.Order.Stop)

                    if d.close[0] < self.inds[ticker]['rolling_low'][-1] or d.close[0] < self.inds[ticker]["sma_slow"]:
                        try:
                            order = self.add_order(data=d, target=0, type='market')
                            self.log('Long Sell Signal')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                elif current_position < 0:
                    if (self.bitcoin.high[0] > self.bitcoin_sma[0]) or (
                            d.high[0] > self.inds[ticker]['rolling_high'][-1]):
                        try:
                            order = self.add_order(data=d, target=0, type="market")
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                if current_position == 0:
                    volatility = self.inds[ticker]["average_true_range"][0] / d.close[0]
                    volatility_factor = 1 / (volatility * 100)
                    closes_above_sma = 0
                    for lookback in [0, -1, -2, -3, -4]:
                        if d.close[lookback] > self.inds[ticker]['sma_veryslow'][lookback]:
                            closes_above_sma += 1
                    if closes_above_sma == 5:
                        if d.close[0] > self.inds[ticker]['sma_fast'][0]:
                            if d.high[0] > self.inds[ticker]['rolling_high'][-1] and d.close[0] > \
                                    self.inds[ticker]['sma_highs'][0]:
                                try:
                                    self.add_order(data=d, target=(
                                                (self.p.order_target_percent / 100) * volatility_factor),
                                                                          type="market")
                                    self.pos[ticker]["sl_price"] = 0.1 * d.close[0]
                                    self.pos[ticker]["new_sl_price"] = None
                                    self.stop_order[ticker] = self.close(data=d, price=self.pos[ticker]["sl_price"], exectype=bt.Order.Stop)
                                except Exception as e:
                                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                                    self.log("{}".format(e))
                    #
                    # elif self.bitcoin.close[0] < self.bitcoin_sma[0]:
                    #     if d.low[0] < self.inds[ticker]['rolling_low'][-1]:
                    #         if self.inds[ticker]['sma_veryfast'][0] < self.inds[ticker]['sma_mid'][0] and self.inds[ticker]['sma_slow'][0] < self.inds[ticker]['sma_veryslow'][0]:
                    #             try:
                    #                 self.orders[ticker] = [self.add_order(data=d, target=-(self.p.order_target_percent/100) * volatility_factor, type="market")]
                    #             except Exception as e:
                    #                 self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #                 self.log("{}".format(e))
            if len(self.to_place_orders) > 0:
                order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                for order_chunk in order_chunks:
                    self.place_batch_order(order_chunk)

    def rebalance_portfolio(self):
        self.rankings = list(filter(lambda d: len(d) > 500, self.altcoins))
        self.rankings.sort(key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]))
        # Rebalance any coins in lowest momentum that are in positions
        for i, d in enumerate(self.rankings[:5]):
            current_position = self.get_position(d=d, attribute='size')
            if current_position:
                try:
                    self.add_order(data=d, target=abs(self.inds[d._name]["roc"][0]), type="market")
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))
