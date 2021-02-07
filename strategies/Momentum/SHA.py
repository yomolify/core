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
        ('order_target_percent', 100)
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
                    if self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] \
                            and (self.inds[ticker]['sha'].lines.sha_close[0] - self.inds[ticker]['sha'].lines.sha_open[0]) > (self.inds[ticker]['sha'].lines.sha_close[-1] - self.inds[ticker]['sha'].lines.sha_open[-1]) \
                            and self.inds[ticker]['pcy'][0] > 0.05 \
                            and self.inds[ticker]['pcy'][0] < 0.95 \
                            and (self.inds[ticker]['pcy'][0] - self.inds[ticker]['pcy'][-1] > 0.08):
                        try:
                            self.orders[ticker] = [
                                self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                                               type="market")]
                            # self.orders[ticker] = [self.add_order(data=d, target=self.p.order_target_percent/100, type="market")]
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))

                    # if self.inds[ticker]['sha'].lines.sha_close[0] < self.inds[ticker]['sha'].lines.sha_open[0] and (self.inds[ticker]['sha'].lines.sha_open[0] - self.inds[ticker]['sha'].lines.sha_close[0]) > (self.inds[ticker]['sha'].lines.sha_open[-1] - self.inds[ticker]['sha'].lines.sha_close[-1]):
                    #     try:
                    #         # self.orders[ticker] = [
                    #             # self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                    #             #                type="market")]
                    #         self.orders[ticker] = [self.add_order(data=d, target=-self.p.order_target_percent/100, type="market")]
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
