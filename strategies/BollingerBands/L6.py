import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase

class L6(StrategyBase):
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
        cross_down_bb_top = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.top)
        cross_down_bb_bot = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.bot)
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
        self.low = 0
    
    def update_indicators(self):
        self.sl_price = 0.95*self.low
        if self.data.close[0] <= self.sl_price:
            self.stop_loss = True

        self.profit = 0
        if self.position.size and self.buy_price_close and self.buy_price_close > 0:
            self.profit = self.data0.close[0] - self.buy_price_close
            self.profit_percentage = (self.profit/self.buy_price_close)*100
            if (self.profit_percentage > 20):
                self.sl_price = 1.15*self.buy_price_close
                self.stop_loss = True
            elif (self.profit_percentage > 25):
                self.sl_price = 1.20*self.buy_price_close
                self.stop_loss = True
            elif (self.profit_percentage > 30):
                self.sl_price = 1.25*self.buy_price_close
                self.stop_loss = True
            elif (self.profit_percentage > 35):
                self.sl_price = 1.30*self.buy_price_close    
                self.stop_loss = True
            elif (self.profit_percentage > 40):
                self.sl_price = 1.35*self.buy_price_close
                self.stop_loss = True

    def next(self):
        self.update_indicators()
        if self.order:
            return

        if not self.position:
            if self.buy_sig:
                if self.data0.close[0] > self.sma_fast[0]:
                    if self.bollinger_bands_width < self.vli_top:
                        if self.low_volatility_level:
                            if self.sma_mid > self.sma_veryslow:
                                self.low = self.data0.low[0]
                                self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                                self.buy_price_close = self.data0.close[0]
                        else:
                            self.low = self.data0.low[0]
                            self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                            self.buy_price_close = self.data0.close[0]

        if self.close_sig:
            self.tp_price = self.data0.close[0]
            self.exec_trade(direction="close", exectype=self.params.exectype)
        
        if self.stop_loss:
            self.stop_loss = False
            self.exec_trade(direction="close", exectype=self.params.exectype)
