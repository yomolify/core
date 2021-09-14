import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING, DEVELOPMENT
from indicators.swing import Swing
import datetime as dt
import math
class SwingHL(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_sma_bitcoin', 250),
        ('period_sma_veryfast', 10),
        ('period_sma_fast', 240),
        ('period_sma_mid', 50),
        ('period_sma_slow', 1200),
        ('period_sma_highs', 20),
        ('period_sma_lows', 8),
        ('order_target_percent', 1)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.strategy = "SwingHL"
        self.order_fraction = 50*len(self.datas)
        self.i = 0
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.long_entrys = {}
        self.long_tps = {}
        self.orders = dict()
        self.pos = {}
        self.flags = {}


        self.entry_bar_height = {}
        if ENV == DEVELOPMENT:
            self.check_for_live_data = False
        else:
            self.check_for_live_data = True

        for d in self.datas:
            ticker = d._name
            self.inds[ticker] = {}
            self.pos[ticker] = {}
            self.entry_bar_height[ticker] = None
            self.long_entrys[ticker] = []
            self.long_tps[ticker] = []
            self.orders[ticker] = []
            self.flags[ticker] = {}
            for i in range(10, -100, -1):
                self.flags[ticker][f"added_on_dip_{i}"] = False
            # self.inds[ticker]["rolling_high"] = bt.indicators.Highest(d.close, period=self.params.period_rolling_high, plot=False, subplot=False)
            # self.inds[ticker]["rolling_low"] = bt.indicators.Lowest(d.close, period=self.params.period_rolling_low, plot=False, subplot=False)
            # self.inds[ticker]["sma_veryfast"] = bt.ind.SimpleMovingAverage(d.close,
            #     period=self.params.period_sma_veryfast, plot=False)
            self.inds[ticker]["sma_fast"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_fast, plot=True)
            # self.inds[ticker]["sma_mid"] = bt.ind.SimpleMovingAverage(d.close,
            #     period=self.params.period_sma_mid, plot=False)
            self.inds[ticker]["sma_slow"] = bt.ind.SimpleMovingAverage(d.close,
                period=self.params.period_sma_slow, plot=True)
            # self.inds[ticker]["sma_veryslow"] = bt.ind.SimpleMovingAverage(d.close,
            #     period=self.params.period_sma_veryslow, plot=False)
            # self.inds[ticker]["sma_highs"] = bt.ind.SimpleMovingAverage(d.high,
            #     period=self.params.period_sma_highs, plot=False)
            # self.inds[ticker]["sma_lows"] = bt.ind.SimpleMovingAverage(d.low,
            #     period=self.params.period_sma_lows, plot=False)
            self.inds[ticker]["atr"] = bt.indicators.AverageTrueRange(d, plot=False, subplot=False)
            self.inds[ticker]["rsi"] = bt.ind.RSI(d, plot=False)
            self.inds[ticker]["adx"] = bt.ind.ADX(d, plot=False)
            # self.inds[ticker]["zerolag"] = bt.ind.ZeroLagExponentialMovingAverage(d, plot=False)
            # self.inds[ticker]["ema"] = bt.ind.EMA(d, plot=False)
            self.inds[ticker]["roc"] = bt.ind.ROC(d, plot=False)
            self.inds[ticker]["swing"] = Swing(d, plot=True, subplot=True)
            # self.inds[ticker]["buy_sig"] = bt.ind.CrossUp(self.inds[ticker]["zerolag"], self.inds[ticker]["ema"])
            # self.inds[ticker]["sell_sig"] = bt.ind.CrossDown(self.inds[ticker]["zerolag"], self.inds[ticker]["ema"])

    def next(self):
        if (self.check_for_live_data and self.status == "LIVE") or not self.check_for_live_data:
            # if self.i % 20 == 0:
            #     self.rebalance_portfolio()
            # self.i += 1
            available = list(filter(lambda d: len(d) > 1, self.altcoins))
            available.sort(reverse=True, key=lambda d: (self.inds[d._name]["rsi"][0]) * (self.inds[d._name]["adx"][0]) * (self.inds[d._name]["roc"][0]))
            for i, d in enumerate(available):
                ticker = d._name
                current_position = self.get_position(d=d, attribute='size')
                entry_price = self.get_position(d=d, attribute='price')
                # if self.inds[ticker]["sma_fast"][0] < self.inds[ticker]["sma_slow"][0]:
                #     self.close(d)
                if current_position > 0:
                    self.pos[ticker]["price"] = self.get_position(d=d, attribute='price')
                    self.pos[ticker]["profit"] = d.close[0] - self.pos[ticker]["price"]
                    self.pos[ticker]["profit_percentage"] = (self.pos[ticker]["profit"] / self.pos[ticker][
                        "price"]) * 100
                    # if self.pos[ticker]["profit_percentage"] < -10h:
                    if self.pos[ticker]["profit_percentage"] < 0 and math.trunc(self.pos[ticker]["profit_percentage"]) % 10 == 0 and not self.flags[ticker][f"added_on_dip_{math.trunc(self.pos[ticker]['profit_percentage'])}"] and math.trunc(self.pos[ticker]['profit_percentage']):
                        value = self.broker.getvalue()
                        max_buyable = value / d.close[0]
                        self.log(f'{ticker} adding on dip at {self.pos[ticker]["profit_percentage"]}')
                        valid = self.data.datetime.date(0) + dt.timedelta(days=1)
                        self.orders[ticker].append(self.buy(d, size=abs(math.trunc(self.pos[ticker]["profit_percentage"]))/10 * 0.5 * max_buyable / self.order_fraction, exectype=bt.Order.Limit, price=d.close[-7] - 0.1 * self.inds[ticker]["atr"][0], valid=valid))
                        self.orders[ticker].append(self.buy(d, size=abs(math.trunc(self.pos[ticker]["profit_percentage"]))/10 * max_buyable / self.order_fraction, exectype=bt.Order.Limit, price=d.close[-7] - self.inds[ticker]["atr"][0], valid=valid))
                        self.orders[ticker].append(self.buy(d, size=abs(math.trunc(self.pos[ticker]["profit_percentage"]))/10 * 2 * max_buyable / self.order_fraction, exectype=bt.Order.Limit, price=d.close[-7] - 2 * self.inds[ticker]["atr"][0], valid=valid))
                        self.flags[ticker][f"added_on_dip_{math.trunc(self.pos[ticker]['profit_percentage'])}"] = True

                # if current_position == 0:
                    # volatility = self.inds[ticker]["atr"][0]/d.close[0]
                    # volatility_factor = 1/(volatility*100)
                if self.inds[ticker]['swing'].lines.signal[0] == -1.0 and self.inds[ticker]["sma_fast"][0] > self.inds[ticker]["sma_slow"][0]:
                # if self.inds[ticker]['buy_sig'] == 1:
                    try:
                        volatility = self.inds[ticker]["atr"][0] / d.close[0]
                        volatility_factor = 1 / (volatility * 100)
                        self.entry_bar_height[ticker] = self.inds[ticker]["atr"][0]/2
                        self.log(f'Long entrys at {d.close[-7]} and {d.close[-7]-self.inds[ticker]["atr"][0]}')
                        value = self.broker.getvalue()
                        max_buyable = (value/d.close[0]) * volatility_factor
                        self.log(f'{ticker} {max_buyable}')
                        # self.order_target_percent(data=d, target=((self.p.order_target_percent / 100) * volatility_factor), exectype=bt.Order.Limit, price=d.close[-7])
                        # self.order_target_percent(data=d, target=((self.p.order_target_percent / 100) * volatility_factor), exectype=bt.Order.Limit, price=d.close[-7]-self.inds[ticker]["atr"][0])
                        # self.order_target_percent(data=d, target=((self.p.order_target_percent / 100) * volatility_factor), exectype=bt.Order.Limit, price=d.close[-7]-2*self.inds[ticker]["atr"][0])
                        # divide by 15 for eth
                        # 128 and 54 without TIF
                        valid = self.data.datetime.date(0) + dt.timedelta(days=1)
                        self.orders[ticker].append(self.buy(d, size=0.5*max_buyable/self.order_fraction, exectype=bt.Order.Limit, price=d.close[-7]-0.1*self.inds[ticker]["atr"][0], valid=valid))
                        self.orders[ticker].append(self.buy(d, size=max_buyable/self.order_fraction, exectype=bt.Order.Limit, price=d.close[-7]-self.inds[ticker]["atr"][0], valid=valid))
                        self.orders[ticker].append(self.buy(d, size=2*max_buyable/self.order_fraction, exectype=bt.Order.Limit, price=d.close[-7]-2*self.inds[ticker]["atr"][0], valid=valid))
                        # self.buy(d, size=8, exectype=bt.Order.Limit, price=d.close[-7])
                        # self.buy(d, size=8, exectype=bt.Order.Limit, price=d.close[-7] - self.inds[ticker]["atr"][0])
                        # self.long_entrys[ticker].append(self.buy(d, size=1, exectype=bt.Order.Limit, price=d.close[-7]-self.inds[ticker]["atr"][0]))
                        # self.orders[ticker] = [self.add_order(data=d, target=((self.p.order_target_percent/100) * volatility_factor), type="market")]
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))


                    # elif self.bitcoin.close[0] < self.bitcoin_sma[0]:
                    #     if d.low[0] < self.inds[ticker]['rolling_low'][-1]:
                    #         if self.inds[ticker]['sma_veryfast'][0] < self.inds[ticker]['sma_mid'][0] and self.inds[ticker]['sma_slow'][0] < self.inds[ticker]['sma_veryslow'][0]:
                    #             try:
                    #                 self.orders[ticker] = [self.add_order(data=d, target=-(self.p.order_target_percent/100) * volatility_factor, type="market")]
                    #             except Exception as e:
                    #                 self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #                 self.log("{}".format(e))
            if len(self.to_place_orders) > 0:
                order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                for order_chunk in order_chunks:
                    self.place_batch_order(order_chunk)
