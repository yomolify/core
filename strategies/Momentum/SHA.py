import backtrader as bt
import sys

from indicators.swing import Swing
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT
from indicators.smoothedHeikinAshi import SmoothedHeikinAshi
from indicators.pcy import PCY

class SHA(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('period_sha_ema', 6),
        ('period_fast_ema', 10),
        ('period_slow_ema', 20),
        ('order_target_percent', 100),
        ('period_sma_slow', 200),
        ('period_roc_sma_fast', 10),
        ('period_roc_sma_slow', 50),
        ('period_roc_sma_veryslow', 200),
        ('period_vol_sma_slow', 200),
        ('period_vol_sma_fast', 50),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        ('period_vol_sma', 50),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.orders = dict()
        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            self.inds[ticker] = {}
            self.inds[ticker]["sha"] = SmoothedHeikinAshi(d, plot=True, subplot=False)
            self.inds[ticker]["pcy"] = PCY(d, plot=True, subplot=True)
            self.inds[ticker]["atr"] = bt.indicators.AverageTrueRange(d, plot=False)
            self.inds[ticker]["vol_sma"] = bt.ind.HullMovingAverage(d.volume,
                                                                    period=self.params.period_vol_sma,
                                                                    plot=True, subplot=True)
            self.inds[ticker]["sma_slow"] = bt.ind.SimpleMovingAverage(d.close,
                                                                       period=self.params.period_sma_slow, plot=False)

            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)

            self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=False)
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


    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            available = list(filter(lambda d: len(d) > 6, self.altcoins))
            for i, d in enumerate(available):
                ticker = d._name

                current_position = self.get_position(d, attribute="size")
                if current_position > 0:
                    # if self.inds[ticker]['sha'].lines.sha_close[0] < self.inds[ticker]['sha'].lines.sha_open[0] and self.inds[ticker]['sha'].lines.sha_low[0] < self.inds[ticker]['sha'].lines.sha_high[0]:
                    if (self.inds[ticker]['sha'].lines.sha_close[0] < self.inds[ticker]['sha'].lines.sha_open[0] \
                            or (self.inds[ticker]['sha'].lines.sha_close[0] - self.inds[ticker]['sha'].lines.sha_open[0]) < (self.inds[ticker]['sha'].lines.sha_close[-1] - self.inds[ticker]['sha'].lines.sha_open[-1])) \
                            and self.inds[ticker]['pcy'][0] > 0.05 \
                            and self.inds[ticker]['pcy'][0] < 0.95 \
                            and (self.inds[ticker]['pcy'][0] - self.inds[ticker]['pcy'][-1] < -0.05):
                        try:
                            order = self.add_order(data=d, target=0, type='market')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                if current_position < 0:
                    # if self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] and self.inds[ticker]['sha'].lines.sha_high[0] > self.inds[ticker]['sha'].lines.sha_low[0]:
                    if (self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] \
                            or (self.inds[ticker]['sha'].lines.sha_open[0] - self.inds[ticker]['sha'].lines.sha_close[0]) < (self.inds[ticker]['sha'].lines.sha_open[-1] - self.inds[ticker]['sha'].lines.sha_close[-1])) \
                            and self.inds[ticker]['pcy'][0] > 0.05\
                            and self.inds[ticker]['pcy'][0] < 0.95\
                            and (self.inds[ticker]['pcy'][0] - self.inds[ticker]['pcy'][-1] < -0.05):

                        try:
                            order = self.add_order(data=d, target=0, type='market')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                if current_position == 0:
                    volatility = self.inds[ticker]["atr"][0] / d.close[0]
                    volatility_factor = 1 / (volatility * 100)
                    volatility_factor = 0.99
                    # if self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] and self.inds[ticker]['sha'].lines.sha_high[0] > self.inds[ticker]['sha'].lines.sha_low[0]:
                    # if self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] \
                    #         and (self.inds[ticker]['sha'].lines.sha_close[0] - self.inds[ticker]['sha'].lines.sha_open[0]) > (self.inds[ticker]['sha'].lines.sha_close[-1] - self.inds[ticker]['sha'].lines.sha_open[-1]) \
                    #         and self.inds[ticker]['pcy'][0] > 0.05 \
                    #         and self.inds[ticker]['pcy'][0] < 0.95 \
                    #         and (self.inds[ticker]['pcy'][0] - self.inds[ticker]['pcy'][-1] > 0.08):
                    #     try:
                    #         self.orders[ticker] = [
                    #             self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                    #                            type="market")]
                    #         # self.orders[ticker] = [self.add_order(data=d, target=self.p.order_target_percent/100, type="market")]
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
                    # elif d.volume[0] > self.inds[ticker]['vol_sma'][0] and d.close[0] > self.inds[ticker]['sma_slow'][0] - 2 * self.inds[ticker]["atr"][0] and self.inds[ticker]['rsi'][0] < 80 or self.inds[ticker]['rsi'][0] < 20:
                    #     try:
                    #         self.orders[ticker] = [
                    #             self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                    #                            type="market")]
                    #         # self.orders[ticker] = [self.add_order(data=d, target=self.p.order_target_percent/100, type="market")]
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
                    # elif self.inds[ticker]["roc_sma_slow"][0] < 0 and self.inds[ticker]["roc_sma_slow"][0] > self.inds[ticker]["roc_sma_slow"][-1] and d.volume[0] > self.inds[ticker]['vol_sma_slow'][0] or self.inds[ticker]["rsi"][0] < 20:
                    #     try:
                    #         self.orders[ticker] = [
                    #             self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                    #                            type="market")]
                    #         # self.orders[ticker] = [self.add_order(data=d, target=self.p.order_target_percent/100, type="market")]
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
                    if self.inds[ticker]['sha'].lines.sha_close[0] < self.inds[ticker]['sha'].lines.sha_open[0] \
                            and (self.inds[ticker]['sha'].lines.sha_open[0] - self.inds[ticker]['sha'].lines.sha_close[0]) > (self.inds[ticker]['sha'].lines.sha_open[-1] - self.inds[ticker]['sha'].lines.sha_close[-1]) \
                            and self.inds[ticker]['pcy'][0] == 1:
                            # and self.inds[ticker]['pcy'][0] < 0.95 \
                            # and (self.inds[ticker]['pcy'][0] - self.inds[ticker]['pcy'][-1] < -0.05):
                        try:
                            # self.orders[ticker] = [
                                # self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                                #                type="market")]
                            self.orders[ticker] = [self.add_order(data=d, target=-self.p.order_target_percent/100, type="market")]
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
