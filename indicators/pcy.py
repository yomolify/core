
import backtrader as bt
from backtrader.indicators import EMA, SMA, Lowest, Highest, HMA


class PCY(bt.Indicator):
    params = (('period_ema', 6),
              ('period_fast_ema', 10),
              ('period_slow_ema', 20),
              ('pcy_alpha', 0.7),
              )
    lines = ('pcy', 'delta')

    def __init__(self):
        self.addminperiod(self.p.period_slow_ema + 1)
        self.M = EMA(self.data.close, period=self.p.period_fast_ema)
        self.m = EMA(self.data.close, period=self.p.period_slow_ema)
        # self.delta = self.M - self.m

        self.min_diff = Lowest(self.M - self.m, period=10)
        self.max_diff = Highest(self.M - self.m, period=10)
        self.delta = (self.max_diff - (self.M - self.m)) / (self.max_diff - self.min_diff)
        # self.lines.pcy = 0
        plotlines = dict(pcy=dict(ls='--'),
                         delta=dict(ls='--'))

    def _plotlabel(self):
            # This method returns a list of labels that will be displayed
            # behind the name of the indicator on the plot

            # The period must always be there
            plabels = [self.p.period_fast_ema]

            return plabels

    def nextstart(self):  # calculate here the seed value
        self.lines.pcy[0] = 0

    def next(self):
        self.lines.pcy[0] = self.p.pcy_alpha * (self.delta[0] - self.pcy.get(ago=-1)[0]) + self.pcy.get(ago=-1)[0]
        # self.lines.delta[0] = self.delta[0]







































# import backtrader as bt
# from backtrader.indicators import SMA, Lowest, Highest
#
#
# class PCY(bt.Indicator):
#     params = (
#         ('period_fast_ema', 10),
#         ('period_slow_ema', 20),
#               )
#     # lines = ('pcy')
#     lines = ('M')
#
#     def __init__(self):
#         # + 1 cuz SHA sees the previous
#         self.addminperiod(self.p.period_slow_ema + 1)
#         self.M = SMA(self.data.close, period=self.p.period_fast_ema)
#         self.m = SMA(self.data.close, period=self.p.period_slow_ema)
#         # self.min_diff = Lowest(self.M - self.m, period=5)
#         # self.max_diff = Highest(self.M - self.m, period=5)
#         # self.delta = SMA((self.max_diff - (self.M - self.m)) / (self.max_diff - self.min_diff), period=1)
#         # self.pcy = 0
#         plotlines = dict(pcy=dict(ls='--'))
#
#
#     def _plotlabel(self):
#             # This method returns a list of labels that will be displayed
#             # behind the name of the indicator on the plot
#
#             # The period must always be there
#             plabels = [self.p.period_fast_ema]
#
#             return plabels
#
#     def next(self):
#         # self.lines.pcy[0] = 1 * (self.delta[0] - self.pcy.get(ago=-1)[0]) + self.pcy.get(ago=-1)[0]
#         # self.lines.pcy[0] = 1
#         self.lines.M[0] = self.M[0]
#         #
#         # self.lines.sha_open[0] = (self.ema_o.get(ago=-1)[0] + self.ema_c.get(ago=-1)[0]) / 2
#         # self.lines.sha_low[0] = min(self.ema_l[0], self.ema_o[0], self.ema_c[0])
#         # self.lines.sha_high[0] = max(self.ema_h[0], self.ema_o[0], self.ema_c[0])
#         # self.lines.sha_close[0] = (self.ema_o[0] + self.ema_h[0] + self.ema_l[0] + self.ema_c[0]) / 4
#
