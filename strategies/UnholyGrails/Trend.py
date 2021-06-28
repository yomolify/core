import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT
import datetime as dt
from indicators.SuperTrend import SuperTrend
from indicators.VWAP import VWAP
from indicators.Momentum import Momentum
# Find top 10 fast moving coins and keep allocation to top 10 at all times
class Trend(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_rolling_high', 120),
        ('period_rolling_low', 120),
        ('period_sma_bitcoin', 250),
        ('period_sma_veryfast', 10),
        ('period_vol_sma', 50),
        ('period_sma_fast', 7),
        ('period_sma_mid', 20),
        ('period_sma_midslow', 100),
        ('period_sma_slow', 200),
        ('period_sma_veryslow', 250),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        ('order_target_percent', 5)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.strategy = "Trend"
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.pos = {}
        self.just_sold = {}
        self.blocked_for = {}
        self.stop_orders = dict()
        self.orders = dict()
        self.entry_bar_height = {}
        self.entry_type = {}
        self.stop_orders = {}
        self.tp_orders = {}
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
            self.stop_orders[ticker] = []
            self.tp_orders[ticker] = []
            self.pos[ticker] = {}
            self.just_sold[ticker] = False
            self.blocked_for[ticker] = 0
            self.inds[ticker] = {}
            self.inds[ticker]["momentum"] = Momentum(d.close, period=90, plot=True, plotname='mom')

            self.inds[ticker]["momentum"].plotinfo.plotname = 'mom'
            self.inds[ticker]["momentum_sma"] = bt.ind.SMA(self.inds[ticker]["momentum"], period=20, plot=True, subplot=True, plotmaster=self.inds[ticker]["momentum"])
            self.inds[ticker]["momentum_sma"].plotlines.sma.color = 'green'
            # self.inds[ticker]["momentum_sma"].plotinfo.plotmaster = 'mom'
            # self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.high, period=self.params.period_rolling_high, plot=True, subplot=False)
            # self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.low, period=self.params.period_rolling_low, plot=True, subplot=False)
            # self.inds[ticker]["atr"] = bt.indicators.AverageTrueRange(d, plot=False)
            # self.inds[ticker]["vwap"] = VWAP(d, period=288, plot=True)
            # self.inds[ticker]["sma_veryfast"] = bt.ind.SimpleMovingAverage(d.close,
            #     period=self.params.period_sma_veryfast, plot=False)
            self.inds[ticker]["sma_fast"] = bt.ind.EMA(d.close,
                period=self.params.period_sma_fast, plot=True)
            self.inds[ticker]["sma_mid"] = bt.ind.EMA(d.close,
                period=self.params.period_sma_mid, plot=True)
            # self.inds[ticker]["sma_midslow"] = bt.ind.SimpleMovingAverage(d.close,
            #                                                           period=self.params.period_sma_midslow, plot=True)
            # self.inds[ticker]["sma_slow"] = bt.ind.SimpleMovingAverage(d.close,
            #     period=self.params.period_sma_slow, plot=True)
            # self.inds[ticker]["sma_veryslow"] = bt.ind.SimpleMovingAverage(d.close,
            #     period=self.params.period_sma_veryslow, plot=True)
            # self.inds[ticker]["sma_highs"] = bt.ind.SimpleMovingAverage(d.high,
            #     period=self.params.period_sma_highs, plot=False)
            # self.inds[ticker]["sma_lows"] = bt.ind.SimpleMovingAverage(d.low,
            #     period=self.params.period_sma_lows, plot=False)
            # self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=False)
            self.inds[ticker]["atr"] = bt.ind.AverageTrueRange(d, plot=False)
            # self.inds[ticker]["adx"] = bt.ind.ADX(d, plot=False)
            # self.inds[ticker]["adx_20"] = bt.ind.ADX(d, period=20, plot=False)
            # self.inds[ticker]["sma_adx_20"] = bt.ind.HMA(self.inds[ticker]["adx_20"], period=20, plot=False, subplot=False)
            # self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)
            # self.inds[ticker]["sma_roc"] = bt.ind.HMA(self.inds[ticker]["roc"], plot=False)
            # self.inds[ticker]["super_trend"] = SuperTrend(d, plot=False, subplot=False)
            # self.inds[ticker]["vol_sma"] = bt.ind.HullMovingAverage(d.volume,
            #                                                         period=self.params.period_vol_sma,
            #                                                         plot=False, subplot=False)


    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            # if self.i % 5 == 0:
            #     self.rebalance_portfolio()
            if self.i % 10 == 0:
                self.rebalance_positions()
            self.i += 1

            available = list(filter(lambda d: len(d) > 100, self.altcoins))
            available.sort(reverse=True, key=lambda d: self.inds[d._name]["momentum"][0])
            top10 = available[:10]
            top15 = available[:15]
            top20 = available[:20]
            for i, d in enumerate(available):
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                if current_position:
                    if d not in top15:
                        self.log(f"Closing {ticker}")
                        self.close(d)
            # self.log('---- top10')
            for i, d in enumerate(top10):
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                self.pos[ticker]["size"] = self.get_position(d=d, attribute='size')
                self.pos[ticker]["price"] = self.get_position(d=d, attribute='price')
                if current_position == 0 and self.inds[ticker]["sma_fast"][0] > self.inds[ticker]["sma_mid"][0]:
                    # volatility = self.inds[ticker]["atr"][0] / d.close[0]
                    # volatility_factor = 1 / (volatility * 100)
                    self.log(f'{ticker} {self.inds[ticker]["momentum"][0]}')
                    try:
                        self.orders[ticker] = [self.add_order(data=d, target=0.066, type="market")]
                        self.pos[ticker]["sl_price"] = 0
                        self.pos[ticker]["new_sl_price"] = None
                        self.pos[ticker]["profit_percentage"] = 0
                        self.pos[ticker]["reset_stop"] = False
                        self.log(f'Long {ticker}')
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                    # d.volume[0] > self.inds[ticker]['vol_sma'][0] and d.close[0] > self.inds[ticker]['sma_slow'][0] - 2 * self.inds[ticker]["atr"][0] and self.inds[ticker]['rsi'][0] < 80
                    # elif d.volume[0] > 3*self.inds[ticker]["vol_sma"][0] and d.close[0] < d.open[0]:
                    #     self.entry_type[ticker] = "Short"
                    #     try:
                    #         self.orders[ticker] = [self.add_order(data=d, target=-0.05, type="market")]
                    #         self.pos[ticker]["sl_price"] = d.close[0] + self.inds[ticker]["atr"][0]
                    #         self.pos[ticker]["new_sl_price"] = None
                    #         self.pos[ticker]["profit_percentage"] = 0
                    #         self.pos[ticker]["reset_stop"] = False
                    #         self.log(f'Short {ticker}')
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))
            if len(self.to_place_orders) > 0:
                order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                for order_chunk in order_chunks:
                    self.place_batch_order(order_chunk)

    def rebalance_positions(self):
        num_stocks = len(self.altcoins)

        # rebalance all stocks
        for i, d in enumerate(self.altcoins[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            self.log(f'value is {value}')
            self.log(f'cash is {cash}')
            size = value * 0.001 / self.inds[d._name]["atr"]
            self.log(f'size is {size}')
            self.order_target_size(d, size)