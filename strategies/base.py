from datetime import datetime
import backtrader as bt
from termcolor import colored
from config import DEVELOPMENT, BASE, QUOTE, ENV, PRODUCTION, DEBUG
from utils import send_telegram_message

# Implementation of exec_trade, notifications & logging 
class StrategyBase(bt.Strategy):
    def __init__(self):
        self.sl_price = None
        self.tp_price = None
        self.stop_loss = False
        self.order = None
        self.last_operation = "SELL"
        self.status = "DISCONNECTED"
        self.buy_price_close = None
        self.log("Base strategy initialized")

    def reset_sell_indicators(self):
        self.buy_price_close = None

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        print(self.status)
        if status == data.LIVE:
            self.log("LIVE DATA - Ready to trade")

    def exec_trade(self, direction, exectype, size=None):
        color = ('red', 'green')[direction=='buy']
        price = self.data0.close[0]

        if ENV != PRODUCTION:
            self.log("{} ordered @ ${}".format(direction.capitalize(), price))
        
        if ENV == PRODUCTION:
            # BUY/SELL BASE coin for QUOTE
            target = (BASE, QUOTE)[direction=='buy']
            cash, value = self.broker.get_wallet_balance(target)
            self.log('{} available: {}'.format(target, cash), color='yellow')

            # QUOTE amount
            # amount = (value / price) * 0.99  # Workaround to avoid precision issues
            amount = ((cash, cash/price)[direction=='buy'])*0.99

            # amount = 0.4  # Workaround to avoid precision issues
            self.log("%sing %s for %s! \nPrice: $%.2f \nAmount: %.6f %s \nBalance: $%.2f USDT" % (direction.capitalize(), BASE, QUOTE, price,
                                                                              amount, BASE, value), True, color)

        if direction == "buy":
            if ENV == DEVELOPMENT:
                return self.buy(size=size, exectype=exectype)
            return self.buy(size=amount, exectype=exectype)
        elif direction == "sell":
            if ENV == DEVELOPMENT:
                return self.sell(size=size, exectype=exectype)
            return self.sell(size=amount, exectype=exectype)
        elif direction == "close":
            if ENV == DEVELOPMENT:
                return self.close(size=size, exectype=exectype)
            return self.close(size=amount, exectype=exectype)

    def notify_order(self, order):
        if order.status in [order.Submitted]:
            # Buy/Sell order submitted to/by broker - Nothing to do
            self.log('ORDER SUBMITTED')
            self.order = order
            return

        if order.status in [order.Accepted]:
            # Buy/Sell order accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED')
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED', True)

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.last_operation = "BUY"
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost (BTC): %.2f, Cost (USD): %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value/order.executed.price,
                     order.executed.value,
                     order.executed.comm), True)
                if ENV == PRODUCTION:
                    print(order.__dict__)

            else:  # Sell
                self.last_operation = "SELL"
                self.reset_sell_indicators()
                self.log('SELL EXECUTED, Price: %.2f, Cost (BTC): %.2f, Cost (USD): %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value/order.executed.price,
                          order.executed.value,
                          order.executed.comm), True)

            # Sentinel to None: new orders allowed
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected: Status %s - %s' % (order.Status[order.status],
                                                                         self.last_operation), True)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        color = 'green'
        if trade.pnl < 0:
            color = 'red'

        self.log(colored('OPERATION PROFIT, GROSS %.2f, NET %.2f\n' % (trade.pnl, trade.pnlcomm), color), True)

    def log(self, txt, send_telegram=False, color=None, highlight=None, attrs=None):
        if not DEBUG:
            return
        # Uncomment for detailed logs
        # return
        value = datetime.now()
        if len(self) > 0:
            value = self.data0.datetime.datetime()

        if color:
            txt = colored(txt, color, highlight, attrs)

        print('[%s] %s' % (value.strftime("%d-%m-%y %H:%M"), txt))
        if send_telegram:
            send_telegram_message(txt)
    
    def start(self):
        if ENV == PRODUCTION:
            self.val_start = (self.broker.get_wallet_balance(BASE))[0]
            self.log('BASE currency available: {} {}'.format(self.val_start, BASE), color='yellow')
            self.quote_available = (self.broker.get_wallet_balance(QUOTE))[0]
            self.log('QUOTE currency available: {} {}'.format(self.quote_available, QUOTE), color='yellow')

        else:
            self.val_start = self.broker.get_cash()

    def stop(self):
        # Calculate ROI
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('\nROI:        {:.2f}%'.format(100.0 * self.roi))  

