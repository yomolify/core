# import backtrader as bt
# from scipy.stats import linregress
# import numpy as np
#
#
# class Momentum(bt.Indicator):
#     lines = ('trend',)
#     params = (('period', 90),)
#     plotlines = dict(Momentum=dict(alpha=0.50, linestyle='-.', linewidth=2.0))
#
#     def __init__(self):
#         self.addminperiod(self.params.period)
#
#     def next(self):
#         returns = np.log(self.data.get(size=self.p.period))
#         x = np.arange(len(returns))
#         slope, _, rvalue, _, _ = linregress(x, returns)
#         annualized = (1 + slope) ** 100
#         self.lines.trend[0] = annualized * (rvalue ** 2)
#
#


import backtrader as bt
import numpy as np
from scipy.stats import linregress


@staticmethod
def momentum_func(data):
    r = np.log(data)
    slope, _, rvalue, _, _ = linregress(np.arange(len(r)), r)
    # annualized = (1 + slope) ** 252
    annualized = (np.power(np.exp(slope), 365) - 1) * 100
    return annualized * (rvalue ** 2)


class Momentum(bt.ind.OperationN):
    lines = ('trend',)
    params = dict(period=20)
    func = momentum_func
