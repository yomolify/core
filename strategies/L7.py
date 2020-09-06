import backtrader as bt
import datetime

class L7(bt.Strategy):
    params = (
        ('period_bb_sma', 20),
        ('period_bb_std', 2),
        ('period_vol_sma_fast', 10),
        ('period_vol_sma_slow', 50),
        ('period_bbw_sma_fast', 10),
        ('period_bbw_sma_slow', 50),
        ('period_bbw_sma_vli_fast', 200),
        ('period_bbw_sma_vli_slow', 500),
        ('period_bbw_stddev', 500),
        ('period_macd_ema_fast', 12),
        ('period_macd_ema_slow', 26),
        ('period_macd_ema_signal', 9),
        ('period_sma_fast', 10),
        ('period_sma_mid', 50),
        ('period_sma_slow', 100),
        ('period_sma_veryslow', 200),
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
            period=self.params.period_bb_sma, devfactor=self.params.period_bb_std, plot=False)
        self.sma_fast = bt.ind.SMA(
            period=self.params.period_sma_fast, plot=False)
        self.sma_mid = bt.ind.SMA(
            period=self.params.period_sma_mid, plot=False)
        self.sma_slow = bt.ind.SMA(
            period=self.params.period_sma_slow, plot=False)
        self.sma_veryslow = bt.ind.SMA(
            period=self.params.period_sma_veryslow, plot=False)

        # Tried crossover / crossdown instead of manually checking - the performance is worse
        # cross_down_bb_top = bt.ind.CrossDown(self.datas[0], self.bollinger_bands.lines.top)
        # cross_down_bb_bot = bt.ind.CrossDown(self.datas[0], self.bollinger_bands.lines.bot)

        # cross_down_bb_top = bt.ind.CrossOver(self.datas[0], self.bollinger_bands.lines.top)
        # cross_down_bb_bot = bt.ind.CrossOver(self.datas[0], self.bollinger_bands.lines.bot)

        cross_down_bb_top = self.datas[0] < self.bollinger_bands.lines.top
        cross_down_bb_bot = self.datas[0] < self.bollinger_bands.lines.bot
     
        volSMA_slow = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_slow, plot=False)
        volSMA_fast = bt.ind.SMA(self.data.volume, subplot=True, period = self.params.period_vol_sma_fast, plot=False)

        vol_condition = volSMA_fast > volSMA_slow

        self.bollinger_bands_width = (self.bollinger_bands.lines.top - self.bollinger_bands.lines.bot)/self.bollinger_bands.lines.mid
        # bbwSMA_slow = bt.ind.SMA(bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_slow, plot=False)
        # bbwSMA_fast = bt.ind.SMA(bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_fast, plot=False)
        # bbw_condition = bbwSMA_slow > bbwSMA_fast

        vli_fast = bt.ind.SMA(self.bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_vli_fast, plot=False)
        vli_slow = bt.ind.SMA(self.bollinger_bands_width, subplot=True, period = self.params.period_bbw_sma_vli_slow, plot=False)
        
        self.vli_top = vli_slow + 2*bt.ind.StdDev(self.bollinger_bands_width, period=self.params.period_bbw_stddev)
        self.low_volatility_level = vli_fast < vli_slow

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
                    if self.bollinger_bands_width < self.vli_top:
                        if self.low_volatility_level:
                            if self.sma_mid > self.sma_veryslow:
                                self.order = self.buy()
                                self.buy_price_close = self.data0.close[0]
                        else:
                            self.order = self.buy()
                            self.buy_price_close = self.data0.close[0]
                    elif self.sma_slow > self.sma_veryslow:
                        self.order = self.buy()
                        self.buy_price_close = self.data0.close[0]
                        # print('========================================+++++++')

                        # SL at low of last candle
                        # Never hit
                        if self.data.close[0] < self.data0.low[-1]:
                            self.close()
                        # Reduces yeild
                        if self.profit_percentage > 3:
                            self.close_price = 1.01*self.buy_price_close
                        


        if self.close_sig:
            # print('close signal')
            self.close()
        # STOP LOSS - 5% below low of entry of entry candle
        # if self.data.close[0] <= 0.65*self.low:
        #     # print('stoploss')
        #     self.close()
        # STOP WIN
        # if self.data0.close[0] <= self.close_price:
        #     # print('stopwin')
        #     self.close()

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