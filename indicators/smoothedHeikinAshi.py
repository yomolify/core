import backtrader as bt
from backtrader.indicators import EMA


class SmoothedHeikinAshi(bt.Indicator):
    params = (('period_ema', 6),)
    lines = ('sha_open', 'sha_low', 'sha_high', 'sha_close')

    def __init__(self):
        # + 1 cuz SHA sees the previous
        self.addminperiod(self.p.period_ema + 1)
        self.ema_o = EMA(self.data.open, period=self.p.period_ema)
        self.ema_c = EMA(self.data.close, period=self.p.period_ema)
        self.ema_h = EMA(self.data.high, period=self.p.period_ema)
        self.ema_l = EMA(self.data.low, period=self.p.period_ema)
        plotlines = dict(sha_open=dict(ls='--'))

    def _plotlabel(self):
            # This method returns a list of labels that will be displayed
            # behind the name of the indicator on the plot

            # The period must always be there
            plabels = [self.p.period_ema]

            return plabels

    def next(self):
        self.lines.sha_open[0] = (self.ema_o.get(ago=-1)[0] + self.ema_c.get(ago=-1)[0]) / 2
        self.lines.sha_low[0] = min(self.ema_l[0], self.ema_o[0], self.ema_c[0])
        self.lines.sha_high[0] = max(self.ema_h[0], self.ema_o[0], self.ema_c[0])
        self.lines.sha_close[0] = (self.ema_o[0] + self.ema_h[0] + self.ema_l[0] + self.ema_c[0]) / 4

