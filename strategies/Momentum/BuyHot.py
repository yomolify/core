import collections
from strategies.base import StrategyBase

import backtrader as bt
from backtrader.indicators import MovingAverageSimple

# from indicators.Momentum import Momentum

import backtrader as bt
import numpy as np
import pandas as pd
# from scipy import stats

class BuyHot(StrategyBase):
    params = dict(
        exectype=bt.Order.Market,
        selcperc=0.10,  # percentage of stocks to select from the universe
        rperiod=2,  # period for the returns calculation, default 1 period
        vperiod=36,  # lookback period for volatility - default 36 periods
        mperiod=24,  # lookback period for strategy - default 12 periods
        reserve=0.05  # 5% reserve capital
    )

    def __init__(self):
        self.dataclose = self.datas[0].close

        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.open_orders = {}
        self.window = 0
        self.started = False

        self.sl_price = None
        self.new_sl_price = None
        self.tp_price = None
        self.profit_percentage = None
        self.long_order = None
        self.long_stop_order = None
        self.short_order = None
        self.short_stop_order = None
        self.stop_order = None
        self.slow_sma_stop_win = False
        self.last_operation = "SELL"
        self.status = "DISCONNECTED"
        self.buy_price_close = None
        self.sell_price_close = None
        self.executed_size = None
        self.strategy = None
        self.entry_bar_height = None
        self.to_place_orders = []
        self.first_bar_after_entry = dict()
        # self.inds = collections.defaultdict(dict)
        self.inds = {}

        for d in self.datas:
            self.inds[d] = {}
            # self.inds[d]["sma200"] = bt.indicators.SMA(d.close, period=200, plot=False, subplot=False)
            # self.inds[d]["pct_change"] = bt.indicators.PctChange(d.close, period=5, plot=False, subplot=False)

        # calculate 1st the amount of stocks that will be selected
        self.selnum = int(len(self.datas) * self.p.selcperc)

        # allocation per stock
        # reserve kept to make sure orders are not rejected due to
        # margin. Prices are calculated when known (close), but orders can only
        # be executed next day (opening price). Price can gap upwards
        self.perctarget = (1.0 - self.p.reserve) % self.selnum

        # returns, volatilities and strategy
        rs = [bt.ind.PctChange(d, period=self.p.rperiod) for d in self.datas]
        # vs = [bt.ind.StdDev(ret, period=self.p.vperiod) for ret in rs]
        # ms = [bt.ind.ROC(d, period=self.p.mperiod) for d in self.datas]

        # simple rank formula: (strategy * net payout) / volatility
        # the highest ranked: low vol, large strategy, large payout
        # self.ranks = {d: 5 * m / v for d, v, m in zip(self.datas, vs, ms)}
        # self.ranks = {d: 5 * 1 / v for d, v in zip(self.datas, vs)}
        self.ranks = {d: r for d, r in zip(self.datas, rs)}

        self.started = False


    def next(self):

        self.started = True
        # sort data and current rank
        ranks = sorted(
            self.ranks.items(),  # get the (d, rank), pair
            key=lambda x: x[1][0],  # use rank (elem 1) and current time "0"
            reverse=True  # highest ranked 1st ... please
        )

        # put top ranked in dict with data as key to test for presence
        rtop = dict(ranks[:self.selnum])
        # For logging purposes of stocks leaving the portfolio
        rbot = dict(ranks[self.selnum:])

        # prepare quick lookup list of stocks currently holding a position
        posdata = [d for d, pos in self.getpositions().items() if pos]

        # remove those no longer top ranked
        # do this first to issue sell orders and free cash
        for d in (d for d in posdata if d not in rtop or rtop[d][0] < 0.04):
            # self.log('Exit {} - Rank {:.2f}'.format(d._name, rbot[d][0]))
            self.order_target_percent(d, target=0.0)

        # rebalance those already top ranked and still there
        for d in (d for d in posdata if d in rtop):
            self.log('Rebal {} - Rank {:.2f}'.format(d._name, rtop[d][0]))
            self.order_target_percent(d, target=self.perctarget)
            del rtop[d]  # remove it, to simplify next iteration

        # issue a target order for the newly top ranked stocks
        # do this last, as this will generate buy orders consuming cash
        for d in rtop:
            if rtop[d][0] > 0.04:
                self.log('Enter {} - Rank {:.2f}'.format(d._name, rtop[d][0]))
                self.order_target_percent(d, target=self.perctarget)

    # def notify_order(self, order):
    #     if order.alive():
    #         return
    #
    #     otypetxt = 'Buy ' if order.isbuy() else 'Sell'
    #     if order.status == order.Completed:
    #         self.log(
    #             '{} Order Completed - Size: {} @Price: {} Value: {:.2f} Comm: {:.2f}'.format(
    #                 otypetxt, order.executed.size, order.executed.price,
    #                 order.executed.value, order.executed.comm
    #             ))
        # else:
        #     self.log('{} Order rejected'.format(otypetxt))

    # def log(self, arg):
    #     print(f'{self.datetime.date(), arg}')
