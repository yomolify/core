import collections
from strategies.base import StrategyBase

import backtrader as bt
from backtrader.indicators import MovingAverageSimple

from indicators.Momentum import Momentum

import backtrader as bt
import numpy as np
import pandas as pd
from scipy import stats

class LinReg(StrategyBase):
    params = dict(stop_loss=0.02,
                  exectype=bt.Order.Market,
                  maximum_stake=0.2,
                  trail=False,
                  volatility_window=20,
                  minimum_momentum=40,
                  portfolio_size=2,
                  reserve=0.05)

    def __init__(self):
        self.dataclose = self.datas[0].close

        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.open_orders = {}
        self.window = 0
        self.started = False

        self.perctarget = (1.0 - self.p.reserve) % self.p.portfolio_size

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
        # self.sma = bt.ind.SMA(self.data, period=self.p.vol_period)
        # self.momentum = self.p.momentum(self.sma, period=self.p.momentum_period)
        # pct_change = bt.ind.PctChange(self.sma, period=self.p.vol_period)
        # self.volatility = bt.ind.StdDev(pct_change, period=self.p.vol_period)

    def next(self):

        self.started = True

        self.window = self.window + 1

        if self.window <= self.p.volatility_window:
            return

        hist, ranking_table = self.calculate_ranking_table()

        kept_positions = self.alter_kept_positions(ranking_table)

        replacement_stocks = self.p.portfolio_size - len(kept_positions)

        buy_list = ranking_table.loc[~ranking_table.index.isin(kept_positions)][:replacement_stocks]

        new_portfolio = self.get_new_portfolio(buy_list, ranking_table, kept_positions)

        if len(kept_positions) > 0 and not self.is_trading_day():
            new_portfolio = new_portfolio.iloc[0:0]

        for symbol in kept_positions:
            new_portfolio = new_portfolio.append({'symbol': symbol, 'ranking': ranking_table.loc[symbol]},
                                                 ignore_index=True)
        new_portfolio.drop_duplicates(subset='symbol', keep='first')

        vola_target_weights = self.calculate_target_weights(hist, new_portfolio)

        self.buy_logic(kept_positions, new_portfolio, ranking_table, vola_target_weights)

    def is_trading_day(self):
        return self.datas[0].datetime.date(0).weekday() == 6

    def volatility(self, data):
        return data.pct_change().rolling(self.p.volatility_window).std().iloc[-1]

    def calculate_ranking_table(self):
        df = pd.DataFrame()
        for datum in self.datas:
            hist = datum.close.lines[0].get(size=self.p.volatility_window + 1)
            df[datum._name] = hist
        ranking_table = df.apply(self.momentum_score).sort_values(ascending=False)
        return df, ranking_table

    def calculate_target_weights(self, df, new_portfolio):
        vola_table = df[new_portfolio['symbol']].apply(self.volatility)
        inv_vola_table = 1 / vola_table
        sum_inv_vola = np.sum(inv_vola_table)
        vola_target_weights = inv_vola_table / sum_inv_vola
        return vola_target_weights.apply(lambda x: min(x, self.p.maximum_stake))

    def buy_logic(self, kept_positions, new_portfolio, ranking_table, vola_target_weights):
        for i, rank in new_portfolio.iterrows():
            symbol = rank['symbol']
            weight = vola_target_weights[symbol]
            if symbol in kept_positions or ranking_table[symbol] > self.p.minimum_momentum:
                dataticker = None
                for x in self.datas:
                    if x.p.name == symbol:
                        dataticker = x
                # if self.inds[dataticker]
                # Only trade when above sma 200, exit if below
                self.open_orders[symbol] = self.order_target_percent(
                    data=dataticker,
                    target=weight, symbol=symbol)

    def get_new_portfolio(self, buy_list, ranking_table, kept_positions):
        new_portfolio = pd.DataFrame(columns=["symbol", "ranking"])
        for i in range(len(buy_list)):
            if ranking_table.iloc[i] and ranking_table.index[i] not in kept_positions:
                new_portfolio.loc[i] = [ranking_table.index[i], ranking_table.iloc[i]]
        if len(new_portfolio) > 10:
            print(new_portfolio)
        return new_portfolio

    def alter_kept_positions(self, ranking_table):
        kept_positions = list(self.open_orders.keys())
        for symbol, security in self.open_orders.items():
            if symbol not in ranking_table or ranking_table[symbol] < self.p.minimum_momentum:
                dataticker = None
                for x in self.datas:
                    if x.p.name == symbol:
                        dataticker = x
                self.open_orders[symbol] = self.close(
                    data=dataticker,
                    symbol=symbol)
                kept_positions.remove(symbol)
        return kept_positions

    # def rebalance(context, hist):
    #     # output_progress(context)
    #     return hist.apply(momentum_score).sort_values(ascending=False)

    def momentum_score(self, data):
        x = np.arange(len(data))
        log_ts = np.log(data)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_ts)
        annualized_slope = (np.power(np.exp(slope), 365) - 1) * 100
        return annualized_slope * (r_value ** 2)


    def output_progress(context):
        perf_pct = (context.portfolio.portfolio_value / context.last_month) - 1
        print("{} - Last Month Result: {:.2%}".format(context.todays_date, perf_pct))
        context.last_month = context.portfolio.portfolio_value
