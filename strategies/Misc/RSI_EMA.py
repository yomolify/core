import backtrader as bt
import backtrader_addons as bta
import datetime

class RSA_EMA(bt.Strategy):
    params = (
        ('exectype', bt.Order.Market),
        ('period_ema_fast', 10),
        ('period_ema_slow', 100)
    )

    # def log(self, txt, dt=None):
    #     ''' Logging function for this strategy'''
    #     dt = dt or self.datas[0].datetime.date(0)
    #     print('%s, %s' % (dt.isoformat(), txt))

    def log(self, txt, send_telegram=False, color=None):
        # if not DEBUG:
        #     return
        return

        value = datetime.datetime.now()
        if len(self) > 0:
            value = self.data0.datetime.datetime()

        if color:
            txt = colored(txt, color)

        print('[%s] %s' % (value.strftime("%d-%m-%y %H:%M"), txt))
        # if send_telegram:
        #     send_telegram_message(txt)

    
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
        # if not trade.isclosed:
        #     return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

        # print('trade.justopened', trade.justopened)
        # print('trade', trade)
        if trade.justopened:
            self.position_bar = trade.baropen
            self.position_highest = float('-inf')

    def __init__(self):
        self.position_bar = None
        self.position_highest = None
        self.stop_loss = False
        self.sl_price = None
        self.tp_price = None
        self.buy_price_close = 0
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a SMA indicator
        
        self.ema_fast = bt.indicators.EMA(period=self.p.period_ema_fast)
        self.ema_slow = bt.indicators.EMA(period=self.p.period_ema_slow)
        self.rsi = bt.indicators.RelativeStrengthIndex()
  
        self.buy_sig = bt.And(self.rsi < 30, self.ema_fast > self.ema_slow)
        self.sell_sig = self.rsi > 70


        self.low = 0

    def start(self):
        self.val_start = self.broker.get_cash()

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('\nROI:        {:.2f}%'.format(100.0 * self.roi))  

    def next(self):
        self.update_indicators()

        # print('self.position_bar', self.position_bar)

        if self.position_bar:
            self.position_highest = max(self.position_highest, self.data.high[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.buy_sig:
                self.order = self.buy(exectype=self.params.exectype)
                self.buy_price_close = self.data0.close[0]
            
            elif self.sell_sig:
                self.order = self.sell(exectype=self.params.exectype)
                self.sell_price_close = self.data0.close[0]

        if self.profit < -0.03:
            self.log("STOP LOSS: percentage %.3f %%" % self.profit)
            self.sell()

    def update_indicators(self):
        # Position size is in BTC
        # Profit is in USD
        self.profit = 0
        if self.buy_price_close and self.buy_price_close > 0:
            self.profit = float(self.data0.close[0] - self.buy_price_close) / self.buy_price_close
        # # LONG
        # if self.position.size > 0:
        #     self.sl_price = 0.95*self.low
        #     self.profit = self.data0.close[0] - self.buy_price_close
        #     self.profit_percentage = (self.profit/self.buy_price_close)*100
        #     if (self.profit_percentage > 20):
        #         self.sl_price = 1.15*self.buy_price_close
        #     elif (self.profit_percentage > 25):
        #         self.sl_price = 1.20*self.buy_price_close
        #     elif (self.profit_percentage > 30):
        #         self.sl_price = 1.25*self.buy_price_close
        #     elif (self.profit_percentage > 35):
        #         self.sl_price = 1.30*self.buy_price_close    
        #     elif (self.profit_percentage > 40):
        #         self.sl_price = 1.35*self.buy_price_close
        #     if self.data.close[0] <= self.sl_price:
        #         self.stop_loss = True
        # # SHORT
        # elif self.position.size < 0:
        #     self.sl_price = self.highest_high_slow[0]
        #     self.profit = self.sell_price_close - self.data0.close[0]
        #     self.profit_percentage = (self.profit/self.sell_price_close)*100
        #     if self.profit_percentage > 10:
        #         self.sl_price = self.highest_high_mid[0]
        #     elif self.profit_percentage > 15:
        #         self.sl_price = self.highest_high_fast[0]
        #     if self.data.close[0] >= self.sl_price:
        #         self.stop_loss = True