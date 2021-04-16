import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT
import datetime as dt
from indicators.SuperTrend import SuperTrend

class NewYearlyHighs(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_rolling_high', 500),
        ('period_rolling_low', 500),
        ('period_sma_bitcoin', 250),
        ('period_sma_veryfast', 10),
        ('period_sma_fast', 20),
        ('period_vol_sma', 50),
        ('period_sma_mid', 50),
        ('period_sma_slow', 200),
        ('period_sma_veryslow', 500),
        ('period_sma_veryslow', 500),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        ('order_target_percent', 5)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.strategy = "NewYearlyHighs"
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.orders = dict()
        self.entry_bar_height = {}
        self.entry_type = {}
        self.long_stop_order = {}
        self.blocked_tickers = []
        self.delayed_tickers = []

        self.bitcoin_atr = bt.indicators.AverageTrueRange(self.bitcoin, plot=False)
        self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close-self.bitcoin_atr,
                                                            period=self.params.period_sma_bitcoin, plot=False)
        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            self.entry_bar_height[ticker] = None
            self.entry_type[ticker] = None
            self.long_stop_order[ticker] = None
            self.inds[ticker] = {}
            self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high, plot=False, subplot=False)
            self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low, plot=False, subplot=False)
            self.inds[ticker]["average_true_range"] = bt.indicators.AverageTrueRange(d, plot=False)
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
            self.inds[ticker]["adx"] = bt.ind.ADX(d, plot=False)
            self.inds[ticker]["adx_20"] = bt.ind.ADX(d, period=20, plot=False)
            self.inds[ticker]["sma_adx_20"] = bt.ind.HMA(self.inds[ticker]["adx_20"], period=20, plot=True, subplot=True)
            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=True)
            self.inds[ticker]["sma_roc"] = bt.ind.HMA(self.inds[ticker]["roc"], plot=False)
            self.inds[ticker]["super_trend"] = SuperTrend(d, plot=True, subplot=False)
            self.inds[ticker]["vol_sma"] = bt.ind.HullMovingAverage(d.volume,
                                                                    period=self.params.period_vol_sma,
                                                                    plot=True, subplot=True)

    # def next_open(self):
    #     if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
    #         available = list(filter(lambda d: len(d) > 500, self.altcoins))
    #         available.sort(reverse=True, key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]) * (self.inds[d._name]["roc"][0]))
    #         for i, d in enumerate(available):
    #             ticker = d._name
    #             if "BTC" in ticker:
    #                 print(f"{dt.datetime.now()} ----- Heartbeat Check OK -----")
    #                 # if self.i % 20 == 0:
    #                 #     self.rebalance_portfolio()
    #                 # self.i += 1
    #             current_position = self.get_position(d=d, attribute='size')
    #             if current_position > 0:
    #                 if self.long_stop_order[ticker]:
    #                     self.cancel(self.long_stop_order[ticker])
    #                     self.long_stop_order[ticker] = None
    #                     self.long_stop_order[ticker] = self.sell(data=d, size=current_position, exectype=bt.Order.Stop, price=self.inds[ticker]["super_trend"][0])

    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            available = list(filter(lambda d: len(d) > 500, self.altcoins))
            available.sort(reverse=True, key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]) * (self.inds[d._name]["roc"][0]))
            self.blocked_tickers = []
            for i, d in enumerate(available):
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                if current_position > 0:
                    if self.entry_type[ticker] is None:
                        if d.close[0] > self.inds[ticker]["super_trend"][0]:
                            self.entry_type[ticker] = "SuperTrend"
                        else:
                            self.entry_type[ticker] = "RSI"
                    if self.entry_type[ticker] == "SuperTrend":
                        if d.close[0] < self.inds[ticker]["super_trend"][0] or (d.close[0] < self.inds[ticker]['rolling_low'][-1] or (self.inds[ticker]["sma_adx_20"][0] > 43 and self.inds[ticker]["sma_adx_20"][-1] > self.inds[ticker]["sma_adx_20"][0])):
                            try:
                                order = self.add_order(data=d, target=0, type='market')
                                self.log(f'Trend fin, closing long {ticker}')
                                self.blocked_tickers.append(ticker)
                                # self.delayed_tickers.append(ticker)
                                # self.blocked_tickers.append(ticker)
                            except Exception as e:
                                self.log("ERROR: {}".format(sys.exc_info()[0]))
                                self.log("{}".format(e))
                    if self.entry_type[ticker] == "RSI":
                        if d.close[0] > self.inds[ticker]["super_trend"][0]:
                            self.entry_type[ticker] = "SuperTrend"
                elif current_position < 0:
                    self.log(f'{ticker} NOT SUPPOSED TO BE HERE')
                    if d.close[0] > self.inds[ticker]["super_trend"][0] or self.inds[ticker]["rsi"][0] < 20:
                        try:
                            order = self.add_order(data=d, target=0, type='market')
                            self.blocked_tickers.append(ticker)
                            self.log(f'Trend fin, closing short {ticker}')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                if current_position == 0 and ticker not in self.delayed_tickers:
                    # if self.long_stop_order[ticker]:
                    #     self.cancel(self.long_stop_order[ticker])
                    volatility = self.inds[ticker]["average_true_range"][0]/d.close[0]
                    volatility_factor = 1/(volatility*100)
                    if d.close[0] > self.inds[ticker]["sma_slow"] and d.close[0] > self.inds[ticker]["super_trend"][0]:
                        self.entry_type[ticker] = "SuperTrend"
                        try:
                            self.orders[ticker] = [self.add_order(data=d, target=((self.p.order_target_percent/100) * volatility_factor), type="market")]
                            self.log(f'Longing ST {ticker}')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
                    #         With volume entry - 5035 and 83, without 1970 and 39
                    # d.volume[0] > self.inds[ticker]['vol_sma'][0] and d.close[0] > self.inds[ticker]['sma_slow'][0] - 2 * self.inds[ticker]["average_true_range"][0] and self.inds[ticker]['rsi'][0] < 80
                    elif self.inds[ticker]["rsi"][0] < 20:
                        self.entry_type[ticker] = "RSI"
                        try:
                            self.orders[ticker] = [self.add_order(data=d, target=((self.p.order_target_percent/100) * volatility_factor), type="market")]
                            self.log(f'Longing RSI {ticker}')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
# 1595 and 39
                    # elif d.close[0] < self.inds[ticker]["super_trend"][0]:
                    #     try:
                    #         self.orders[ticker] = [self.add_order(data=d, target=-(self.p.order_target_percent/100) * volatility_factor, type="market")]
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
            print(f"{dt.datetime.now()} ----- Heartbeat Check OK -----")
            if self.i % 20 == 0:
                self.rebalance_portfolio()
                self.delayed_tickers = []
            self.i += 1
            if len(self.to_place_orders) > 0:
                order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                for order_chunk in order_chunks:
                    self.place_batch_order(order_chunk)
    def rebalance_portfolio(self):
        self.rankings = list(filter(lambda d: len(d) > 500, self.altcoins))
        self.rankings.sort(key=lambda d: (self.inds[d._name]["rsi"][0])*(self.inds[d._name]["adx"][0]))
        # Rebalance any coins in lowest momentum that are in positions
        for i, d in enumerate(self.rankings[:10]):
            current_position = self.get_position(d=d, attribute='size')
            self.log(self.blocked_tickers)
            if current_position and d._name not in self.blocked_tickers:
                try:
                    if abs(self.inds[d._name]["roc"][0]) > 0.02:
                        order = self.add_order(data=d, target=abs(self.inds[d._name]["roc"][0]), type="market")
                        self.log(f'Rebalancing {d._name}')
                    else:
                        self.add_order(data=d, target=0, type='market')
                        self.log(f"Dead {d._name}. ROC: {round(abs(self.inds[d._name]['roc'][0]), 3)}, RSI: {round((self.inds[d._name]['rsi'][0]), 1)} ADX: {round((self.inds[d._name]['adx'][0]), 1)} RSI*ADX: {round((self.inds[d._name]['rsi'][0])*(self.inds[d._name]['adx'][0]), 0)}")
                except Exception as e:
                    self.log("ERROR: {}".format(sys.exc_info()[0]))
                    self.log("{}".format(e))