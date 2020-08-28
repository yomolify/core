from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import os.path
import sys  # To find out the script name (in argv[0])

import backtrader as bt

from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
from btplotting import BacktraderPlotting
from btplotting.schemes import Tradimo, Blackly
from termcolor import colored

def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--dataname', default='', required=False,
                        help='File Data to Load')

    parser.add_argument('--timeframe', default='weekly', required=False,
                        choices=['daily', 'weekly', 'monhtly'],
                        help='Timeframe to resample to')

    parser.add_argument('--compression', default=1, required=False, type=int,
                        help='Compress n bars into 1')

    return parser.parse_args()

args = parse_args()

class L1(bt.Strategy):
    params = (
        ('period_bb_sma', 20),
        ('period_bb_std', 2),
        ('period_vol_sma_fast', 10),
        ('period_vol_sma_slow', 50),
        ('period_bbw_sma_fast', 10),
        ('period_bbw_sma_slow', 50),
        ('period_macd_ema_fast', 12),
        ('period_macd_ema_slow', 26),
        ('period_macd_ema_signal', 9),
        ('period_sma_fast', 20),
        ('period_sma_slow', 50),
        ('period_price_channel_break', 20),
        ('maperiod', 15)
    )

    # def log(self, txt, dt=None):
    #     ''' Logging function for this strategy'''
    #     dt = dt or self.datas[0].datetime.date(0)
    #     print('%s, %s' % (dt.isoformat(), txt))

    def log(self, txt, send_telegram=False, color=None):
        # if not DEBUG:
        #     return

        value = datetime.datetime.now()
        if len(self) > 0:
            value = self.data0.datetime.datetime()

        if color:
            txt = colored(txt, color)

        print('[%s] %s' % (value.strftime("%d-%m-%y %H:%M"), txt))
        # if send_telegram:
        #     send_telegram_message(txt)


    def __init__(self):
        self.buy_price_close = 0
        self.close_price = 0
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a SMA indicator
        
        self.bollinger_bands = bt.ind.BollingerBands(
            period=self.params.period_bb_sma, devfactor=self.params.period_bb_std)
        self.sma_fast = bt.ind.SMA(
            period=self.params.period_sma_fast)

        cross_down_bb_top = self.datas[0] < self.bollinger_bands.lines.top
        cross_down_bb_bot = self.datas[0] < self.bollinger_bands.lines.bot
     
        volSMA_slow = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_slow, plot="false")
        volSMA_fast = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_fast, plot="false")

        vol_condition = volSMA_fast > volSMA_slow

        bollinger_bands_width = (self.bollinger_bands.lines.top - self.bollinger_bands.lines.bot)/self.bollinger_bands.lines.mid
        # bbwSMA_slow = bt.ind.SMA(bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_slow, plot="false")
        # bbwSMA_fast = bt.ind.SMA(bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_fast, plot="false")
        # bbw_condition = SMA(BBW, per=10) > SMA(BBW, per=50)
        
        self.buy_sig = bt.And(cross_down_bb_top, vol_condition)
        self.close_sig = bt.And(cross_down_bb_bot, vol_condition)
     
        self.profit = 0
        self.low = 0

        # Indicators for the plotting show
        # bt.ind.BollingerBands(period=self.params.period_bb_sma, devfactor=self.params.period_bb_std)

    def next(self):
        self.update_indicators()

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.buy_sig:
                self.low = self.data0.low[0]
                if self.data0.close[0] > self.sma_fast[0]:
                    self.order = self.buy()
                    self.buy_price_close = self.data0.close[0]

        if self.close_sig:
            self.close()
        # STOP LOSS - 5% below low of entry of entry candle
        if self.data.close[0] <= 0.95*self.low:
            self.close()
        # STOP WIN
        if self.data0.close[0] <= self.close_price:
            self.close()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def update_indicators(self):
        self.profit = 0
        if self.buy_price_close and self.buy_price_close > 0:
            self.profit = float(self.data0.close[0] - self.buy_price_close) / self.buy_price_close
        
        if bool(self.buy_price_close) & bool(self.position):
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



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(L1)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'data/truncated.csv')
    # datapath = os.path.join(modpath, 'data/bitstampUSD_1-min_data_2015-04-01_to_2018-04-01.csv')
    datapath = os.path.join(modpath, 'data/BTCUSDT-1h.csv')

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        # dtformat=lambda x: datetime.datetime.utcfromtimestamp(int(x)),
        # Do not pass values before this date
        # fromdate=datetime.datetime(2016, 4, 1),
        fromdate=datetime.datetime(2017, 8, 17),
        # Do not pass values before this date
        # todate=datetime.datetime(2018, 4, 1),
        # todate=datetime.datetime(2016, 5, 1),
        todate=datetime.datetime(2019, 3, 1),
        nullvalue=0.0,
        # Do not pass values after this date
        reverse=False)

    # Handy dictionary for the argument timeframe conversion
    tframes = dict(
        minutes=bt.TimeFrame.Minutes,
        daily=bt.TimeFrame.Days,
        weekly=bt.TimeFrame.Weeks,
        monthly=bt.TimeFrame.Months)

    # Add the Data Feed to Cerebro
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=360)

    cerebro.resampledata(data,
                         timeframe=tframes["minutes"],
                         compression=60)

    # cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    # fig = cerebro.plot(style='candlestick')[0][0]
    # fig.set_size_inches(18.5, 10.5)
    # fig
    
    # b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    # cerebro.plot(b)

    p = BacktraderPlotting(style='candle', scheme=Blackly())
    cerebro.plot(p)

# self.log('Low => {}'.format(self.low))