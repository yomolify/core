import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase

class L2(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('period_bb_sma', 20),
        ('period_bb_std', 2),
        ('period_vol_sma_fast', 10),
        ('period_vol_sma_slow', 50),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.bollinger_bands = bt.ind.BollingerBands(
            period=self.params.period_bb_sma, devfactor=self.params.period_bb_std, plot=False)
        cross_down_bb_top = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.top)
        cross_down_bb_bot = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.bot)
        volSMA_slow = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_slow, plot=False)
        volSMA_fast = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_fast, plot=False)
        vol_condition = volSMA_fast > volSMA_slow
        self.buy_sig = bt.And(cross_down_bb_top, vol_condition)
        self.close_sig = bt.And(cross_down_bb_bot, vol_condition)
        self.low = 0
    
    def update_indicators(self):
        # Calculate Stop Loss
        self.sl_price = 0.95*self.low
        if self.data.close[0] <= self.sl_price:
            self.stop_loss = True

    def next(self):
        self.update_indicators()
        if self.order:
            return

        if not self.position:
            if self.buy_sig:
                self.low = self.data0.low[0]
                self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
                self.buy_price_close = self.data0.close[0]

        if self.close_sig:
            self.tp_price = self.data0.close[0]
            self.exec_trade(direction="close", exectype=self.params.exectype)
        
        # STOP LOSS - 5% below low of entry of entry candle
        if self.stop_loss:
            self.stop_loss = False
            self.exec_trade(direction="close", exectype=self.params.exectype)
