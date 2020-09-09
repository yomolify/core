import backtrader as bt
import backtrader_addons as bta
import datetime

class L3(bt.Strategy):
    params = (
        ('exectype', bt.Order.Market),
        ('period_bb_sma', 20),
        ('period_bb_std', 2),
        ('period_vol_sma_fast', 10),
        ('period_vol_sma_slow', 50),
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
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def __init__(self):
        self.stop_loss = False
        self.sl_price = None
        self.tp_price = None
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
            period=self.params.period_bb_sma, devfactor=self.params.period_bb_std, plot=False)

        # Tried crossover / crossdown instead of manually checking - the performance is worse
        # cross_down_bb_top = bt.ind.CrossDown(self.datas[0], self.bollinger_bands.lines.top)
        # cross_down_bb_bot = bt.ind.CrossDown(self.datas[0], self.bollinger_bands.lines.bot)

        cross_down_bb_top = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.top)
        cross_down_bb_bot = bt.ind.CrossDown(self.datas[0].close, self.bollinger_bands.lines.bot)

        # cross_down_bb_top = bt.ind.CrossOver(self.datas[0], self.bollinger_bands.lines.top)
        # cross_down_bb_bot = bt.ind.CrossOver(self.datas[0], self.bollinger_bands.lines.bot)

        # cross_down_bb_top = self.dataclose < self.bollinger_bands.lines.top
        # cross_down_bb_bot = self.dataclose < self.bollinger_bands.lines.bot
     
        volSMA_slow = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_slow, plot=False)
        volSMA_fast = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_fast, plot=False)

        vol_condition = volSMA_fast > volSMA_slow

        self.buy_sig = bt.And(cross_down_bb_top, vol_condition)
        self.close_sig = bt.And(cross_down_bb_bot, vol_condition)

        self.low = 0

    def start(self):
        self.val_start = self.broker.get_cash()

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('\nROI:        {:.2f}%'.format(100.0 * self.roi))  

    def next(self):
        self.update_indicators()

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.buy_sig:
                self.low = self.data0.low[0]
                self.order = self.buy(exectype=self.params.exectype)
                self.buy_price_close = self.data0.close[0]

        if self.close_sig:
            self.tp_price = self.data0.close[0]
            self.close(exectype=self.params.exectype)
        
        # STOP LOSS - 5% below low of entry of entry candle
        if self.stop_loss:
            self.stop_loss = False
            self.close(exectype=self.params.exectype)

        # if self.data.close[0] <= 0.95*self.low:
        #     self.sl_price = self.data.close[0]
        #     print('STOP LOSS')

        # STOP WIN
        # if self.data0.close[0] <= self.close_price:
        #     print('STOP WIN')
        #     self.sl_price = self.data.close[0]
        #     self.close(exectype=self.params.exectype)


    def update_indicators(self):
        # Calculate Stop Loss
        self.sl_price = 0.95*self.low
        if self.data.close[0] <= self.sl_price:
            self.stop_loss = True


        # Position size is in BTC
        # Profit is in USD
        self.profit = 0
        if self.position.size and self.buy_price_close and self.buy_price_close > 0:
            # self.profit = float(self.data0.close[0] - self.buy_price_close) / self.buy_price_close
            # self.profit = (self.data0.close[0] - self.buy_price_close)*self.position.size
            self.profit = self.data0.close[0] - self.buy_price_close
            self.profit_percentage = (self.profit/self.buy_price_close)*100

            # print('\nBuy Price Close:', self.buy_price_close)
            # print('Current Price:', self.data0.close[0])
            # print('Profit:', self.profit)
            # print('Size:', self.position.size)
            # print('Profit percentage:', self.profit_percentage)

            # print('self.profit_percentage', self.profit_percentage)
            
            if (self.profit_percentage > 40):
                # print('profit_percentage > 40:', self.profit_percentage)
                self.close_price = 1.35*self.buy_price_close
            elif (self.profit_percentage > 35):
                self.close_price = 1.30*self.buy_price_close                
            elif (self.profit_percentage > 30):
                self.close_price = 1.25*self.buy_price_close
            elif (self.profit_percentage > 25):
                self.close_price = 1.20*self.buy_price_close
            elif (self.profit_percentage > 20):
                self.close_price = 1.15*self.buy_price_close
