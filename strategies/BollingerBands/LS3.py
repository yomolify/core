import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase

class LS3(StrategyBase):
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
        self.position_bar = None
        self.position_highest = None
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
        self.vli_slow = bt.ind.SMA(self.bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_vli_slow, plot=False)
        self.vli_top = self.vli_slow + 2*bt.ind.StdDev(self.bollinger_bands_width, period=self.params.period_bbw_sma_vli_slow)
        self.low_volatility_level = vli_fast < self.vli_slow
        self.buy_sig = bt.And(cross_down_bb_top, vol_condition)
        self.close_sig = bt.And(cross_down_bb_bot, vol_condition)
        self.sell_sig = bt.And(cross_up_bb_bot, vol_condition)
        self.low = 0

    def update_indicators(self):
        self.profit = 0
        # LONG
        if self.position.size > 0:
            self.log('self.buy_price_close in Long: {}'.format(self.buy_price_close))
            
            self.sl_price = 0.95*self.low
            # self.log('self.low in Long: {}'.format(self.low))
            # self.log('self.sl_price in Long: {}'.format(self.sl_price))

            self.profit = self.data0.close[0] - self.buy_price_close
            self.profit_percentage = (self.profit/self.buy_price_close)*100
            if (self.profit_percentage > 40):
                self.log('IN >40')
                self.sl_price = 1.35*self.buy_price_close
                self.stop_loss = True

            elif (self.profit_percentage > 35):
                self.log('IN >35')
                self.sl_price = 1.30*self.buy_price_close  
                self.stop_loss = True

            elif (self.profit_percentage > 30):
                self.log('IN >30')
                self.sl_price = 1.25*self.buy_price_close
                self.stop_loss = True

            elif (self.profit_percentage > 25):
                self.log('IN >25')
                self.sl_price = 1.20*self.buy_price_close
                self.stop_loss = True

            elif (self.profit_percentage > 20):
                self.log('IN >20')
                self.sl_price = 1.15*self.buy_price_close
                self.stop_loss = True

            if self.data.close[0] <= self.sl_price:
                self.stop_loss = True
        # SHORT
        elif self.position.size < 0:
            # self.log('self.position.size in Short: {}'.format(self.position.size))

            self.sl_price = self.highest_high_slow[0]
            # self.log('self.highest_high_slow[0] in Short: ', self.highest_high_slow[0])
            # self.log('self.sell_price_close in Short: {}'.format(self.sell_price_close))
            # self.log('SL Price in Short: ', self.sl_price)

            self.profit = self.sell_price_close - self.data0.close[0]
            self.profit_percentage = (self.profit/self.sell_price_close)*100
            if (self.profit_percentage > 35):
                self.log('IN >35')
                self.log(self.profit_percentage)
                
                self.sl_price = 0.7*self.sell_price_close    
            elif (self.profit_percentage > 30):
                self.log('IN > 30')
                self.log(self.profit_percentage)
                
                self.sl_price = 0.75*self.sell_price_close
                self.stop_loss = True

            elif (self.profit_percentage > 25):
                self.log('IN > 25')
                self.log(self.profit_percentage)
                
                self.sl_price = 0.8*self.sell_price_close
                self.stop_loss = True

            elif self.profit_percentage > 15:
                self.log('IN > 15')
                self.log(self.profit_percentage)
                
                self.sl_price = self.highest_high_fast[0]
                self.stop_loss = True

            elif self.profit_percentage > 10:
                self.log('IN > 10')
                self.log(self.profit_percentage)
                
                self.sl_price = self.highest_high_mid[0]
                self.stop_loss = True

            if self.data.close[0] >= self.sl_price:
                self.stop_loss = True

            
            # elif (self.profit_percentage > 25):
            #     self.sl_price = 1.20*self.sell_price_close
            # elif (self.profit_percentage > 30):
            #     self.sl_price = 1.25*self.sell_price_close
            # elif (self.profit_percentage > 35):
            #     self.sl_price = 1.30*self.sell_price_close    
            # elif (self.profit_percentage > 40):
            #     self.sl_price = 1.35*self.buy_price_close


    def next(self):
        self.update_indicators()
        if self.position_bar:
            self.position_highest = max(self.position_highest, self.data.high[0])
        if self.order:
            return

        if abs(self.broker.getposition(self.datas[0]).size) < 0.01:
            if self.buy_sig:
                if self.data0.close[0] > self.sma_fast[0]:
                    if self.bollinger_bands_width < self.vli_top:
                        if self.low_volatility_level:
                            if self.sma_mid > self.sma_veryslow:
                                self.low = self.data0.low[0]
                                self.log('low volatility')
                                self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                                # self.buy_price_close = self.data0.close[0]
                        else:
                            self.low = self.data0.low[0]
                            self.log('regular volatility')
                            # self.log('self.data0.low[0]: {}'.format(self.data0.low[0]))
                            # self.log('self.low: {}'.format(self.low))
                            self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                            # self.buy_price_close = self.data0.close[0]
                    elif self.sma_slow > self.sma_veryslow:
                        self.low_alt = self.data0.low[-1]
                        self.log('sma_slow > sma_veryslow')
                        self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                        # self.buy_price_close = self.data0.close[0]

                        if self.data.close[0] < self.data0.low[-1]:
                            self.log('self.data.close[0] < self.data0.low[-1]')
                            self.exec_trade(direction="close", exectype=self.params.exectype)
                        if self.profit_percentage > 3:
                            self.sl_price = 1.01*self.buy_price_close
            
            elif self.sell_sig:
                # if self.bollinger_bands_width < self.vli_slow:
                # self.sell_price_close = self.data0.close[0]
                self.order = self.exec_trade(direction="sell", exectype=self.params.exectype)

        if self.stop_loss:
            self.stop_loss = False
            self.log('stop_loss')
            self.exec_trade(direction="close", exectype=self.params.exectype)
        elif self.close_sig:
            self.tp_price = self.data0.close[0]
            self.log('close_sig')
            self.exec_trade(direction="close", exectype=self.params.exectype)
