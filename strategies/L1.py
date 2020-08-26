#!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase
from termcolor import colored

class L1(StrategyBase):
    params = dict(
        period_bb_sma=20,
        period_bb_std=2,
        period_vol_sma_fast=10,
        period_vol_sma_slow=50,
        period_macd_ema_fast=12,
        period_macd_ema_slow=26,
        period_macd_ema_signal=9,
        period_sma_fast=26,
        period_sma_slow=50,
        period_price_channel_break=20,
    )

    def __init__(self):
        self.close_price = 0
        StrategyBase.__init__(self)
        # L1
        self.log("Using L1")
        
        bollinger_bands = bt.indicators.BollingerBands(period=self.p.period_bb_sma, devfactor=self.p.period_bb_std)
        cross_down_bb_top = self.data.close < bollinger_bands.lines.top
        cross_down_bb_bot = self.data.close < bollinger_bands.lines.bot
     
        volSMA_slow = bt.indicators.MovingAverageSimple(self.data.volume, period = self.p.period_vol_sma_slow)
        volSMA_fast = bt.indicators.MovingAverageSimple(self.data.volume, period = self.p.period_vol_sma_fast)

        vol_condition = volSMA_fast > volSMA_slow
        
        # L1
        self.buy_sig = bt.And(cross_down_bb_top, vol_condition)
        self.close_sig = bt.And(cross_down_bb_bot, vol_condition)
     
        self.profit = 0
        self.low = 0

    def update_indicators(self):
        self.profit = 0
        if self.buy_price_close and self.buy_price_close > 0:
            self.profit = float(self.data0.close[0] - self.buy_price_close) / self.buy_price_close
        
        if self.buy_price_close:
            self.profit_percentage = (self.profit/self.position.size)*100
            
            if (self.profit_percentage > 40):
                self.close_price = 1.35*self.buy_price_close
            elif (self.profit_percentage > 35):
                self.close_price = 1.30*self.buy_price_close                
            elif (self.profit_percentage > 30):
                self.close_price = 1.25*self.buy_price_close
            elif (self.profit_percentage > 25):
                self.close_price = 1.20*self.buy_price_close
            elif (self.profit_percentage > 20):
                self.close_price = 1.15*self.buy_price_close
            
    def next(self):
        self.update_indicators()

        if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
            return

        if self.order:  # waiting for pending order
            return
        
        # ----- ORDER MANAGEMENT -----
        
        # LONG - If CrossDown Bollinger Top & vol_condition
        if self.last_operation != "BUY":
            if self.buy_sig:
                self.log('+++++++++++ BUY BUY BUY BUY BUY BUY BUY BUY BUY BUY BUY BUY +++++++++++')
                self.low = self.data0.low[0]
                self.log('Low => {}'.format(self.low))
                self.log('Close => {}'.format(self.data.close[0]))
                self.long()
                self.log(self.position)
        
        # CLOSE
        if self.position.size:
            if self.data0.close[0] <= self.close_price:
                self.log(colored('----------- STOPWIN STOPWIN STOPWIN STOPWIN STOPWIN -----------','blue'), True)
                self.close()
            elif self.close_sig:
                self.log('----------- SELL SELL SELL SELL SELL SELL SELL SELL SELL -----------')
                self.close()
            # STOP LOSS - 5% below low of entry of entry candle
            elif self.data.close[0] <= 0.95*self.low:
                self.log('XXXXXXXXXXX STOP STOP STOP STOP STOP STOP STOP STOP STOP XXXXXXXXXXX')
                self.close()