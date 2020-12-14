import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase
# unoptimized first four periods - 20, 2, 10, 50
class NLS1(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('period_bb_sma', 23),
        ('period_bb_std', 2.5),
        ('period_vol_sma_fast', 14),
        ('period_vol_sma_slow', 54),
        ('period_sma_veryfast', 10),
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
        self.stop_loss_slow_sma = False
        self.sl_price_slow_sma = None
        self.bollinger_bands = bt.ind.BollingerBands(
            period=self.params.period_bb_sma, devfactor=self.params.period_bb_std, plot=False)
        self.sma_veryfast = bt.ind.SMA(
            period=self.params.period_sma_veryfast, plot=False)
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
        # self.log(self.profit_percentage)
        # LONG
        if self.position.size > 0:
            # self.log('self.buy_price_close in Long: {}'.format(self.buy_price_close))
            # self.log('self.low in Long: {}'.format(self.low))
            # self.log('self.sl_price in Long: {}'.format(self.sl_price))

            self.profit = self.data0.close[0] - self.buy_price_close
            self.profit_percentage = (self.profit/self.buy_price_close)*100
            if self.stop_loss_slow_sma == True and not self.slow_sma_stop_win:
                if self.profit_percentage > 3:
                    self.log('slow_sma STOPWIN')
                    self.sl_price_slow_sma = 1.01*self.buy_price_close
                    self.slow_sma_stop_win = True
                    if (self.long_stop_order):
                        self.cancel(self.long_stop_order)
                    self.long_stop_order = self.exec_trade(direction="close", price=self.sl_price_slow_sma, exectype=self.params.exectype)
            if (self.profit_percentage > 45):
                self.log('Long profit > 45%, updating stop win to 40%')
                self.new_sl_price = 1.40*self.buy_price_close
            if (self.profit_percentage > 40):
                self.log('Long profit > 40%, updating stop win to 35%')
                self.new_sl_price = 1.35*self.buy_price_close
            elif (self.profit_percentage > 35):
                self.log('Long profit > 35%, updating stop win to 30%')
                self.new_sl_price = 1.30*self.buy_price_close
            elif (self.profit_percentage > 30):
                self.log('Long profit > 30%, updating stop win to 25%')
                self.new_sl_price = 1.25*self.buy_price_close
            elif (self.profit_percentage > 25):
                self.log('Long profit > 25%, updating stop win to 20%')
                self.new_sl_price = 1.20*self.buy_price_close
            elif (self.profit_percentage > 20):
                self.log('Long profit > 20%, updating stop win to 15%')
                self.new_sl_price = 1.15*self.buy_price_close
            # self.log(self.sl_price)
            # self.log(self.new_sl_price)
            if self.new_sl_price and self.sl_price and self.new_sl_price > self.sl_price:
                self.sl_price = self.new_sl_price
                if self.long_stop_order:
                    self.cancel(self.long_stop_order)
                self.long_stop_order = self.exec_trade(direction="close", price=self.sl_price, exectype=bt.Order.Stop)
            # Emergency close

        # SHORT
        elif self.position.size < 0:
            # self.log('self.position.size in Short: {}'.format(self.position.size))
            # self.new_sl_price = self.highest_high_slow[0]
            # self.log('SL Price in Short: {}'.format(self.sl_price))
            # self.log('self.sell_price_close in Short: {}'.format(self.sell_price_close))
            # if self.new_sl_price < self.sl_price:
            #     self.sl_price = self.new_sl_price
            #     self.cancel(self.stop_order)
            #     self.stop_order = self.exec_trade(direction="buy", price=self.sl_price, exectype=bt.Order.Stop)
            self.new_sl_price = self.highest_high_slow[0]
            self.profit = self.sell_price_close - self.data0.close[0]
            self.profit_percentage = (self.profit/self.sell_price_close)*100
            if (self.profit_percentage > 40):
                self.log('Short profit > 40%, updating stop win to 35%')
                self.new_sl_price = 0.65*self.sell_price_close    
            if (self.profit_percentage > 35):
                self.log('Short profit > 35%, updating stop win to 30%')
                self.new_sl_price = 0.7*self.sell_price_close    
            elif (self.profit_percentage > 30):
                self.log('Short profit > 30%, updating stop win to 25%')
                self.new_sl_price = 0.75*self.sell_price_close
            elif (self.profit_percentage > 25):
                self.log('Short profit > 25%, updating stop win to 20%')
                self.new_sl_price = 0.8*self.sell_price_close
            elif self.profit_percentage > 15:
                self.log('Short profit > 15%, updating stop win to rolling highest high of last 5 hours')
                self.new_sl_price = self.highest_high_fast[0]
            elif self.profit_percentage > 10:
                self.log('Short profit > 10%, updating stop win to rolling highest high of last 10 hours')
                self.new_sl_price = self.highest_high_mid[0]
            # self.log(self.new_sl_price)
            # self.log(self.sl_price)
            if self.new_sl_price and self.sl_price and self.new_sl_price < self.sl_price:
                self.sl_price = self.new_sl_price
                if self.short_stop_order:
                    self.cancel(self.short_stop_order)
                self.short_stop_order = self.exec_trade(direction="close", price=self.sl_price, exectype=bt.Order.Stop)

    def next(self):
        if abs(self.broker.getposition(self.datas[0]).size) > 0.0005:
            if self.close_sig:
                self.long_order = None
                self.short_order = None
                self.sl_price_slow_sma = None
                self.stop_loss_slow_sma = False
                self.slow_sma_stop_win = False
                self.tp_price = self.data0.close[0]
                # Try with low/high below
                self.log('Price closed below bottom bollinger band with high volume. Closing position.')
                self.exec_trade(direction="close", exectype=self.params.exectype)
                # Cancel Stops
                if self.long_stop_order:
                    self.log('Cancelling long stop order')
                    self.cancel(self.long_stop_order)
                    self.long_stop_order = None
                if self.short_stop_order:
                    self.log('Cancelling short stop order')
                    self.cancel(self.short_stop_order)
                    self.short_stop_order = None
            # else:
            self.update_indicators()
            
        # if self.long_order or self.short_order or self.long_stop_order or self.short_stop_order:
        #     return
        if abs(self.broker.getposition(self.datas[0]).size) < 0.0005:
            if self.long_stop_order:
                self.log('Cancelling redundant long stop order')
                self.cancel(self.long_stop_order)
            if self.short_stop_order:
                # Even when the stop order is completed, it tries to cancel
                # self.log(self.short_stop_order.Status)
                self.log('Cancelling redundant short stop order')
                self.cancel(self.short_stop_order)
            self.long_order = None
            self.short_order = None
            self.long_stop_order = None
            self.short_stop_order = None
            self.stop_loss_slow_sma = False
            self.sl_price = None
            self.new_sl_price = None
            self.tp_price = None
            
        if self.long_order or self.short_order:
            return

        if abs(self.broker.getposition(self.datas[0]).size) < 0.0005:
            if self.buy_sig:
                if self.data0.close[0] > self.sma_fast[0]:
                    if self.bollinger_bands_width < self.vli_top:
                        if self.low_volatility_level:
                            if self.sma_mid[0] > self.sma_veryslow[0]:
                                self.long_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                                self.log('Enter Long: Price crossed below upper bollinger band while being > SMA 20 during low volatility & SMA 50 > SMA 200')
                        elif not (self.sma_veryslow[0] > self.sma_slow[0] > self.sma_mid[0]):
                            self.low = self.data0.low[0]
                            self.long_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                            self.log('Enter Long: Price crossed below upper bollinger band while being > SMA 20 during high volatility & not(SMA 200 > 100 > 50)')
                    elif self.sma_slow[0] > self.sma_veryslow[0]:
                        self.long_order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                        self.log('Enter Long: Price crossed below upper bollinger band while being > SMA 20 & SMA 100 > SMA 200')
                        # self.stop_loss_slow_sma = True

            elif self.sell_sig:
                if self.sma_veryfast < self.sma_mid:
                    self.short_order = self.exec_trade(direction="sell", exectype=self.params.exectype)
                    self.log('Enter Short: SMA 10 < SMA 50 & price closed above lower bollinger band with high volume.')
                # self.sl_price = self.highest_high_slow[0]
                # self.short_stop_order = self.exec_trade(direction="buy", price=self.sl_price, exectype=self.params.exectype)
        # Create stop orders
        # self.log(f'self.long_order -----------------------------------: {self.long_order}')
        # self.log(f'self.long_stop_order -----------------------------------: {self.long_stop_order}')
        # self.log(f'self.sl_price_slow_sma -----------------------------------: {self.stop_loss_slow_sma}')
        # self.log(f'BOOLEAN -----------------------------------: {not self.long_stop_order and not self.stop_loss_slow_sma}')
