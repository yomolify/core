import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase

class LS1(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('period_bb_sma', 20),
        ('period_bb_std', 2),
        ('period_vol_sma_fast', 10),
        ('period_vol_sma_slow', 50),
        ('period_sma_fast', 20),
        ('period_sma_mid', 50),
        ('period_sma_slow', 100),
        ('period_sma_veryslow', 200),
        ('period_bbw_sma_fast', 10),
        ('period_bbw_sma_slow', 50),
        ('period_bbw_sma_vli_fast', 200),
        ('period_bbw_sma_vli_slow', 1000),
        ('period_bbw_stddev', 2),
        ('period_bb_sma', 20),
        ('period_bb_std', 2),
        ('period_highest_high_slow', 20),
        ('period_highest_high_mid', 10),
        ('period_highest_high_fast', 5),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.bollinger_bands = bt.ind.BollingerBands(
            period=self.params.period_bb_sma, devfactor=self.params.period_bb_std, plot=False)
        self.sma_fast = bt.ind.SMA(
            period=self.params.period_sma_fast, plot=False)
        self.sma_mid = bt.ind.SMA(
            period=self.params.period_sma_mid, plot=False)
        self.sma_slow = bt.ind.SMA(
            period=self.params.period_sma_slow, plot=False)
        self.sma_veryslow = bt.ind.SMA(
            period=self.params.period_sma_veryslow, plot=False)
        self.highest_high_slow = bt.ind.Highest(
            period=self.params.period_highest_high_slow, plot=False)
        self.highest_high_mid = bt.ind.Highest(
            period=self.params.period_highest_high_mid, plot=False)
        self.highest_high_fast = bt.ind.Highest(
            period=self.params.period_highest_high_fast, plot=False)
        cross_down_bb_top = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.top)
        cross_down_bb_bot = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.bot)
        cross_up_bb_bot = bt.ind.CrossUp(self.datas[0].close, self.bollinger_bands.lines.bot)
        volSMA_slow = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_slow, plot=False)
        volSMA_fast = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_fast, plot=False)
        vol_condition = volSMA_fast > volSMA_slow
        self.bollinger_bands_width = (self.bollinger_bands.lines.top - self.bollinger_bands.lines.bot)/self.bollinger_bands.lines.mid
        vli_fast = bt.ind.SMA(self.bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_vli_fast, plot=False)
        vli_slow = bt.ind.SMA(self.bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_vli_slow, plot=False)
        self.vli_top = vli_slow + 2*bt.ind.StdDev(self.bollinger_bands_width, period=self.params.period_bbw_sma_vli_slow)
        self.low_volatility_level = vli_fast < vli_slow
        self.buy_sig = bt.And(cross_down_bb_top, vol_condition)
        self.close_sig = bt.And(cross_down_bb_bot, vol_condition)
        self.sell_sig = bt.And(cross_up_bb_bot, vol_condition)
        self.low = 0
        self.profit = 0
    
    def update_indicators(self):
        if self.position.size > 0:
            self.profit = self.data0.close[0] - self.buy_price_close
            self.profit_percentage = (self.profit/self.buy_price_close)*100
            if self.sma_slow_entry:
                if self.profit_percentage > 3:
                    self.log('sma_slow stop loss')
                    self.new_sl_price = 1.01*self.buy_price_close
                    self.sma_slow_entry = False
            if (self.profit_percentage > 40):
                self.log('In > 40')
                self.new_sl_price = 1.35*self.buy_price_close
            elif (self.profit_percentage > 35):
                self.log('In > 35')
                self.new_sl_price = 1.30*self.buy_price_close    
            elif (self.profit_percentage > 30):
                self.log('In > 30')
                self.new_sl_price = 1.25*self.buy_price_close
            elif (self.profit_percentage > 25):
                self.log('In > 25')
                self.new_sl_price = 1.20*self.buy_price_close
            elif (self.profit_percentage > 20):
                self.log('In > 20')
                self.new_sl_price = 1.15*self.buy_price_close
            if self.new_sl_price and self.new_sl_price > self.sl_price:
                self.log('LONG self.new_sl_price > self.sl_price')
                self.sl_price = self.new_sl_price
                self.cancel_stop_order = self.exec_trade(direction="cancel", exectype=self.params.exectype, ref=self.stop_order)
                self.stop_order = self.exec_trade(direction="sell", price=self.sl_price, exectype=bt.Order.Stop)
        elif self.position.size < 0:
            self.profit = self.sell_price_close - self.data0.close[0]
            self.profit_percentage = (self.profit/self.sell_price_close)*100
            if self.profit_percentage > 15 and not self.pp15:
                self.log('In > 15')
                self.new_sl_price = self.highest_high_fast[0]
                self.pp15 = True
            elif self.profit_percentage > 10  and not self.pp10:
                self.log('In > 10')
                self.new_sl_price = self.highest_high_mid[0]
                self.pp10 = True
            if self.new_sl_price and self.new_sl_price < self.sl_price:
                self.log(f'self.new_sl_price is {self.new_sl_price}')
                self.log('SHORT self.new_sl_price < self.sl_price')
                self.sl_price = self.new_sl_price
                self.cancel_stop_order = self.exec_trade(direction="cancel", exectype=self.params.exectype, ref=self.stop_order)
                self.stop_order = self.exec_trade(direction="buy", price=self.sl_price, exectype=bt.Order.Stop)


    def next(self):
        self.update_indicators()
        if self.order:
            return

        if not self.position:
            self.sl_price = None
            self.tp_price = None
            self.new_sl_price = None
            self.sma_slow_entry = False
            self.pp15 = False
            self.pp10 = False
            if self.buy_sig:
                if self.data0.close[0] > self.sma_fast[0]:
                    if self.bollinger_bands_width < self.vli_top:
                        if self.low_volatility_level:
                            if self.sma_mid > self.sma_veryslow:
                                self.sl_price = 0.95*self.data0.low[0]
                                self.buy_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                                self.stop_order = self.exec_trade(direction="sell", price=self.sl_price, exectype=bt.Order.Stop)
                        else:
                            self.sl_price = 0.95*self.data0.low[0]
                            self.buy_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                            self.stop_order = self.exec_trade(direction="sell", price=self.sl_price, exectype=bt.Order.Stop)
                    elif self.sma_slow > self.sma_veryslow:
                        self.log('sma_slow entry')
                        self.sl_price = self.data0.low[-1]
                        self.buy_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                        self.stop_order = self.exec_trade(direction="sell", price=self.sl_price, exectype=bt.Order.Stop)
                        self.sma_slow_entry = True
            elif self.sell_sig:
                self.sl_price = self.highest_high_slow[0]
                self.sell_order = self.exec_trade(direction="sell", exectype=self.params.exectype)
                self.stop_order = self.exec_trade(direction="buy", price=self.sl_price, exectype=bt.Order.Stop)

        # Long close condition
        elif self.broker.getposition(self.datas[0]).size > 0.01: 
            if self.close_sig:
                self.tp_price = self.data0.close[0]
                self.log('-----Close Signal-----')
                self.cancel_stop_order = self.exec_trade(direction="cancel", exectype=self.params.exectype, ref=self.stop_order)
                self.close_order = self.exec_trade(direction="close", exectype=self.params.exectype)
                self.sl_price = None