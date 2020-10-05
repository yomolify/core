import backtrader as bt
import datetime
from strategies.base import StrategyBase

class L1(StrategyBase):
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
            period=self.params.period_bb_sma, devfactor=self.params.period_bb_std, plot=True)

        # Tried crossover / crossdown instead of manually checking - the performance is worse
        # cross_down_bb_top = bt.ind.CrossDown(self.datas[0], self.bollinger_bands.lines.top)
        # cross_down_bb_bot = bt.ind.CrossDown(self.datas[0], self.bollinger_bands.lines.bot)

        cross_down_bb_top = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.top)
        cross_down_bb_bot = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.bot)

        # cross_down_bb_top = bt.ind.CrossOver(self.datas[0], self.bollinger_bands.lines.top)
        # cross_down_bb_bot = bt.ind.CrossOver(self.datas[0], self.bollinger_bands.lines.bot)

        # cross_down_bb_top = self.dataclose < self.bollinger_bands.lines.top
        # cross_down_bb_bot = self.dataclose < self.bollinger_bands.lines.bot
     
        volSMA_slow = bt.ind.SMA(self.data.volume, subplot=True, period=self.params.period_vol_sma_slow, plot=True)
        volSMA_fast = bt.ind.SMA(self.data.volume, subplot=True, period=self.params.period_vol_sma_fast, plot=True)

        vol_condition = volSMA_fast > volSMA_slow

        self.buy_sig = bt.And(cross_down_bb_top, vol_condition)
        self.close_sig = bt.And(cross_down_bb_bot, vol_condition)

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.buy_sig:
                self.order = self.exec_trade(direction="buy", exectype=self.params.exectype)
        else:
            if self.close_sig:
                self.order = self.exec_trade(direction="close", exectype=self.params.exectype)
