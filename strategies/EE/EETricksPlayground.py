import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT

class EETricksPlayground(StrategyBase):

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
        ('period_roc_sma_fast', 10),
        ('period_roc_sma_slow', 50),
        ('period_roc_sma_veryslow', 200),
        ('period_vol_sma_slow', 200),
        ('period_vol_sma_fast', 50),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        ('order_target_percent', 100)
    )
    # With otp 4
    # 208.82 and 43
    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.pos = {}
        self.orders = dict()
        self.stop_order = dict()
        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            self.pos[ticker] = {}
            self.inds[ticker] = {}
            self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high, plot=False, subplot=False)
            self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low, plot=False, subplot=False)
            self.inds[ticker]["average_true_range"] = bt.indicators.AverageTrueRange(d, plot=False, subplot=False)
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
            self.inds[ticker]["sma_highs"] = bt.ind.SimpleMovingAverage(d.high,
                period=self.params.period_sma_highs, plot=False)
            self.inds[ticker]["sma_lows"] = bt.ind.SimpleMovingAverage(d.low,
                period=self.params.period_sma_lows, plot=False)
            self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=False)
            self.inds[ticker]["adx"] = bt.ind.ADX(d, period=15, plot=True)
            self.inds[ticker]
            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)
            self.inds[ticker]["roc_sma_veryslow"] = bt.ind.HMA(self.inds[ticker]["roc"],
                                                               period=self.params.period_roc_sma_veryslow, plot=False,
                                                               subplot=False)
            self.inds[ticker]["roc_sma_slow"] = bt.ind.HMA(self.inds[ticker]["roc"],
                                                           period=self.params.period_roc_sma_slow, plot=False,
                                                           subplot=False)
            self.inds[ticker]["roc_sma_fast"] = bt.ind.HMA(self.inds[ticker]["roc"],
                                                           period=self.params.period_roc_sma_fast, plot=False,
                                                           subplot=False)
            self.inds[ticker]["vol_sma_fast"] = bt.ind.HullMovingAverage(d.volume,
                                                                         period=self.params.period_vol_sma_fast,
                                                                         plot=False, subplot=False)
            self.inds[ticker]["vol_sma_slow"] = bt.ind.HullMovingAverage(d.volume,
                                                                         period=self.params.period_vol_sma_slow,
                                                                         plot=False, subplot=False)
            self.inds[ticker]["highest_high"] = bt.ind.Highest(
                period=10, plot=False)
            self.inds[ticker]["lowest_low"] = bt.ind.Lowest(
                period=10, plot=False)

    def updateProfit(self, d):
        ticker = d._name
        current_position = self.get_position(d=d, attribute='size')
        self.pos[ticker]["size"] = self.get_position(d=d, attribute='size')
        self.pos[ticker]["price"] = self.get_position(d=d, attribute='price')
        if current_position > 0:
            self.pos[ticker]["previous_profit_percentage"] = self.pos[ticker]["profit_percentage"]
            self.pos[ticker]["profit"] = d.close[0] - self.pos[ticker]["price"]
            self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker]["price"]) * 100

    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            if self.i % 1 == 0:
                self.rebalance_profits()
            self.i += 1
            available = list(filter(lambda d: len(d) > 500, self.altcoins))
            available.sort(reverse=True, key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]) * (self.inds[d._name]["roc"][0]))
            for i, d in enumerate(available):
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                if current_position > 0:
                    # self.updateStops(d)
                    self.updateProfit(d)
                    if (d.close[0] < self.inds[ticker]['rolling_low'][-1]):
                        try:
                            order = self.add_order(data=d, target=0, type='market')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                elif current_position < 0:
                    if (self.bitcoin.high[0] > self.bitcoin_sma[0]) or (d.high[0] > self.inds[ticker]['rolling_high'][-1]):
                        try:
                            order = self.add_order(data=d, target=0, type="market")
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                if current_position == 0:
                    volatility = self.inds[ticker]["average_true_range"][0]/d.close[0]
                    volatility_factor = 1/(volatility*100)
                    volatility_factor = 0.99
                    closes_above_sma = 0
                    # for lookback in [0, -1, -2, -3, -4]:
                    #     if d.close[lookback] > self.inds[ticker]['sma_veryslow'][lookback]:
                    #         closes_above_sma += 1
                    if self.inds[ticker]["rsi"][0] < 30:
                        try:
                            self.orders[ticker] = [
                                self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                                               type="market")]
                            self.pos[ticker]["sl_price"] = d.close[0] - self.inds[ticker]["average_true_range"][0]
                            self.pos[ticker]["new_sl_price"] = None
                            self.pos[ticker]["profit_percentage"] = 0
                            self.pos[ticker]["reset_stop"] = False
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))

    def rebalance_profits(self):
        self.rankings = list(filter(lambda d: len(d) > 500, self.altcoins))
        # self.rankings.sort(key=lambda d: (self.inds[d._name]["rsi"][0])*(self.inds[d._name]["adx"][0]))
        self.rankings.sort(key=lambda d: (self.inds[d._name]["rsi"][0])*(self.inds[d._name]["adx"][0]))
        # Rebalance any coins in lowest momentum that are in positions
        for i, d in enumerate(self.rankings[:30]):
            current_position = self.get_position(d=d, attribute='size')
            if current_position:
                if self.pos[d._name]["profit_percentage"] > 0.1:
                    try:
                        self.log(f'Closing {d._name} in profit')
                        self.close(d)
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                # elif self.pos[d._name]["profit_percentage"] < -0.1:
                #     try:
                #         self.log(f'Buying {self.pos[d._name]["size"]/3} {d._name} in loss')
                #         self.buy(d, size=self.pos[d._name]["size"]/3)
                #     except Exception as e:
                #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                #         self.log("{}".format(e))