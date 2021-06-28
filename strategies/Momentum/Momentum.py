import collections
from strategies.base import StrategyBase

import backtrader as bt
from backtrader.indicators import MovingAverageSimple

from indicators.Momentum import Momentum

import backtrader as bt
import numpy as np
import pandas as pd
from scipy import stats

class Momentum(StrategyBase):
    params = dict(
        momentum=Momentum,
        exectype=bt.Order.Market,
        momentum_period=20,
        volatr=bt.ind.ATR,
        vol_period=20,
        minimum_momentum=40,
        reserve=0.05,
        maximum_stake=0.2
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
        self.inds = collections.defaultdict(dict)

        for d in self.datas:
            self.inds[d]['strategy'] = self.p.momentum(d, period=self.p.momentum_period)
            self.inds[d]['volatility'] = self.p.volatr(d, period=self.p.vol_period)
            pct_change = bt.ind.PctChange(d, period=self.p.vol_period)
            self.inds[d]['stddev'] = bt.ind.StdDev(pct_change, period=self.p.vol_period)

        self.d_with_len = []
        self.rankings = []

        self.add_timer(when=bt.Timer.SESSION_START, weekdays=[5], weekcarry=True, action='portfolio')
        self.add_timer(when=bt.Timer.SESSION_START, weekdays=[6], weekcarry=True, action='positions')
        # self.sma = bt.ind.SMA(self.data, period=self.p.vol_period)
        # self.momentum = self.p.momentum(self.sma, period=self.p.momentum_period)
        # pct_change = bt.ind.PctChange(self.sma, period=self.p.vol_period)
        # self.volatility = bt.ind.StdDev(pct_change, period=self.p.vol_period)

    def notify_timer(self, timer, when, *args, **kwargs):
        if kwargs['action'] == 'positions':
            self.rebalance_positions()
        elif kwargs['action'] == 'portfolio':
            self.rebalance_portfolio()

    def notify_order(self, order):
        if order.alive():
            return

        otypetxt = 'Buy' if order.isbuy() else 'Sell'
        if order.status == order.Completed:
            self.log(
                '{} Order Completed - Symbol: {} Size: {} @Price: {} Value: {:.2f} Comm: {:.2f}'.format(
                    otypetxt, order.info['symbol'], order.executed.size, order.executed.price,
                    order.executed.value, order.executed.comm
                ))
        else:
            self.log('{} Order rejected'.format(otypetxt))

    def log(self, arg):
        print(f'{self.datetime.date(), arg}')

    def rebalance_portfolio(self):
        # only look at data that we can have indicators for
        self.rankings = list(filter(lambda data: len(data) > self.p.vol_period, self.datas))
        self.rankings.sort(key=lambda data: self.inds[data]["strategy"][0], reverse=True)
        num_stocks = len(self.rankings)

        # sell stocks based on criteria
        for i, d in enumerate(self.rankings):
            if self.getposition(self.data).size:
                if i > num_stocks or d < self.p.minimum_momentum:
                    self.close(d)

        # buy stocks with remaining cash
        for i, d in enumerate(self.rankings[:num_stocks]):
            cash = self.broker.get_cash()

            target_weights = self.calculate_target_weights()

            if cash <= 0:
                break
            if not self.getposition(self.data).size:
                self.order_target_percent(d, target=target_weights[d], symbol=d._name)

    def rebalance_positions(self):
        num_stocks = len(self.rankings)

        # rebalance all stocks
        for i, d in enumerate(self.rankings[:num_stocks]):
            cash = self.broker.get_cash()
            target_weights = self.calculate_target_weights()

            if cash <= 0:
                break
            self.order_target_percent(d, target=target_weights[d], symbol=d._name)

    def volatility(self, data):
        return data.pct_change().rolling(self.p.volatility_window).std().iloc[-1]

    def calculate_target_weights(self):
        num_stocks = len(self.rankings)

        targets = {}
        total_sum = self.p.reserve

        for i, d in enumerate(self.rankings[:num_stocks]):
            target_value = 1 / self.inds[d]["stddev"]
            if np.isnan(target_value):
                targets[d] = 0
            else:
                targets[d] = target_value
                total_sum += target_value

        for k, v in targets.items():
            percentage = targets[k] / total_sum
            targets[k] = percentage

        return targets