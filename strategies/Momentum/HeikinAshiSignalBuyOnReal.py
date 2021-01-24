import backtrader as bt
import sys

from indicators.swing import Swing
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT
from indicators.smoothedHeikinAshi import SmoothedHeikinAshi

class SHA(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('period_sha_ema', 6),
        ('order_target_percent', 100)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        # for i, d in enumerate(self.datas):
        #     if d._name == 'Real':
        #         self.real = d
        #     elif d._name == 'Heikin':
        #         self.heikin = d

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
            if 'Heikin' in d._name:
                ticker = d._name
                self.inds[ticker] = {}
                self.inds[ticker]["sha"] = SmoothedHeikinAshi(d, plot=True, subplot=False)

    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            available = list(filter(lambda d: len(d) > 500, self.altcoins))
            for i, d in enumerate(self.datas):
                if 'Real' in d._name:
                    self.real = d
                elif 'Heikin' in d._name:
                    self.hk = d
            for i, d in enumerate(available):
                ticker = 'Heikin_ETH-USDT'
                current_position = self.get_position(self.real)
                # print(self.inds[ticker]['sha'].lines.sha_open[0])
                # print(self.inds[ticker]['sha'].lines.sha_open[0])
                if current_position > 0:
                    # if self.inds[ticker]['sha'].lines.sha_close[0] < self.inds[ticker]['sha'].lines.sha_open[0] and self.inds[ticker]['sha'].lines.sha_low[0] < self.inds[ticker]['sha'].lines.sha_high[0]:
                    if self.inds[ticker]['sha'].lines.sha_close[0] < self.inds[ticker]['sha'].lines.sha_open[0] or (self.inds[ticker]['sha'].lines.sha_close[0] - self.inds[ticker]['sha'].lines.sha_open[0]) < (self.inds[ticker]['sha'].lines.sha_close[-1] - self.inds[ticker]['sha'].lines.sha_open[-1]):
                        try:
                            order = self.add_order(data=self.real, target=0, type='market')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                if current_position < 0:
                    # if self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] and self.inds[ticker]['sha'].lines.sha_high[0] > self.inds[ticker]['sha'].lines.sha_low[0]:
                    if self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] or (self.inds[ticker]['sha'].lines.sha_open[0] - self.inds[ticker]['sha'].lines.sha_close[0]) < (self.inds[ticker]['sha'].lines.sha_open[-1] - self.inds[ticker]['sha'].lines.sha_close[-1]):
                        try:
                            order = self.add_order(data=self.real, target=0, type='market')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                if current_position == 0:
                    # volatility = self.inds[ticker]["average_true_range"][0] / d.close[0]
                    # volatility_factor = 1 / (volatility * 100)
                    # if self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] and self.inds[ticker]['sha'].lines.sha_high[0] > self.inds[ticker]['sha'].lines.sha_low[0]:
                    if self.inds[ticker]['sha'].lines.sha_close[0] > self.inds[ticker]['sha'].lines.sha_open[0] and (self.inds[ticker]['sha'].lines.sha_close[0] - self.inds[ticker]['sha'].lines.sha_open[0]) > (self.inds[ticker]['sha'].lines.sha_close[-1] - self.inds[ticker]['sha'].lines.sha_open[-1]):
                        try:
                            # self.orders[ticker] = [
                                # self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                                #                type="market")]
                            self.orders[ticker] = [self.add_order(data=self.real, target=self.p.order_target_percent/100, type="market")]
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))

                    # if self.inds[ticker]['sha'].lines.sha_close[0] < self.inds[ticker]['sha'].lines.sha_open[0] and (self.inds[ticker]['sha'].lines.sha_open[0] - self.inds[ticker]['sha'].lines.sha_close[0]) > (self.inds[ticker]['sha'].lines.sha_open[-1] - self.inds[ticker]['sha'].lines.sha_close[-1]):
                    #     try:
                    #         # self.orders[ticker] = [
                    #             # self.add_order(data=d, target=((self.p.order_target_percent / 100) * volatility_factor),
                    #             #                type="market")]
                    #         self.orders[ticker] = [self.add_order(data=d, target=self.p.order_target_percent/100, type="market")]
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
                    if self.inds[ticker]['sha'].lines.sha_close[0] < self.inds[ticker]['sha'].lines.sha_open[0] and self.inds[ticker]['sha'].lines.sha_low[0] < self.inds[ticker]['sha'].lines.sha_high[0]:
                        try:
                            # self.orders[ticker] = [self.add_order(data=d, target=-(self.p.order_target_percent/100) * volatility_factor, type="market")]
                            self.orders[ticker] = [self.add_order(data=self.real, target=-(self.p.order_target_percent/100), type="market")]
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
            # if len(self.to_place_orders) > 0:
            #     order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
            #     for order_chunk in order_chunks:
            #         self.place_batch_order(order_chunk)
