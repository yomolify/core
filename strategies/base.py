import sys
from datetime import datetime, timedelta
import backtrader as bt
from termcolor import colored
from config import DEVELOPMENT, BASE, QUOTE, ENV, PRODUCTION, DEBUG, TRADING
from utils import send_telegram_message

# TODO implement isPosition
LONG = "LONG"

PERCENT = 0.99


# Implementation of exec_trade, notifications & logging 
class StrategyBase(bt.Strategy):
    def __init__(self):
        self.sl_price = None
        self.new_sl_price = None
        self.tp_price = None
        self.profit_percentage = None
        self.long_order = None
        self.long_stop_order = None
        self.short_order = None
        self.short_stop_order = None
        self.stop_order = None
        self.slow_sma_stop_win = False
        self.last_operation = "SELL"
        self.status = "DISCONNECTED"
        self.buy_price_close = None
        self.sell_price_close = None
        self.log("Base strategy initialized", send_telegram=True)
        self.log("Trading: {}".format(TRADING))

    # def reset_sell_indicators(self):
    #     self.buy_price_close = None

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        print(self.status)
        if status == data.LIVE:
            self.log("LIVE DATA - Ready to trade")

    def exec_trade(self, direction, exectype, size=None, ref=None, price=None, oco=None):
        cash = None
        color = ('red', 'green')[direction=='buy']
        close_price = self.data0.close[0]
        # self.log(f'{direction.capitalize()} supplied price is {price}')
        if ENV != PRODUCTION:
            self.log("{} ordered @ ${}".format(direction.capitalize(), close_price))
            amount = size
        # Remove all instances of cash for futures flow because it's all only USDT, so when BASE/QUOTE are inverted there is no BASE cash (since all is USDT)
        if ENV == PRODUCTION:
            self.log('{}'.format(self.position), color='magenta', send_telegram=True)
            # self.log('Data time: {}, Computer Time: {}'.format(self.data0.datetime.datetime(), datetime.now() - timedelta(minutes=63)))
            # Works for minute timeframe
            if self.data0.datetime.datetime() < datetime.now() - timedelta(minutes=63):
            # Works for hourly timeframe
            # if self.data0.datetime.datetime() < datetime.now() - timedelta(minutes=123):
                self.log('Historical data, so not placing real order')
                return
            # BUY/SELL BASE coin for QUOTE
            target = (BASE, QUOTE)[direction=='buy']
            if TRADING == "LIVE":
                # If no position, we are entering long or short
                target = 'USDT'
                if abs(self.broker.getposition(self.datas[0]).size) < 0.0005:
                    if direction=="buy":
                        cash, value = self.broker.get_wallet_balance(target)
                        self.log(f'cash is {cash}')
                    if direction=="sell":
                        cash, value = self.broker.get_wallet_balance(target)
                        self.log(f'cash is {cash}')
                        size = cash/self.data0.close[0]*PERCENT
                        self.log(f'size is {size}')
                
                # If we are in a position, we are in a long/short, so size of close order = position size
                # if abs(self.broker.getposition(self.datas[0]).size) > 0.0005:
                #     if direction=="close":
                #         size = abs(self.broker.getposition(self.datas[0]).size)

                # if target == 'USDT':
                #     cash, value = self.broker.get_wallet_balance(target)
                # else if self.position.size:
                #     size = self.position.size
                # self.log('{} available: {}'.format(target, cash), color='yellow')
            else:
                cash = self.broker.get_cash()
                value = self.broker.get_value()

            if size == None:
                if cash is not None:
                    amount = ((cash, cash/close_price)[direction=='buy'])*PERCENT
            else:
                amount = size
            # If we are in a position, we are in a long/short, so size of close order = position size. Close automatically uses size from position size
            if TRADING == "LIVE" and direction=="close":
                size = None
            # Hack for correct logs while paper trading
            if TRADING == "PAPER":
                if direction != "buy":
                    amount = self.position.size
            # self.log('''
            #     %sing %.2f %s for %.2f %s!
            #     close_Price: $%.2f
            #     Amount: %.2f %s
            #     Cost: %.2f %s'''
            #     % (direction.capitalize(), amount, BASE, close_price*amount, QUOTE, close_price, amount, BASE, close_price*amount, QUOTE), True, color)
                # Balance: $%.2f USDT
                
        try:
            if direction == "buy":
                self.last_operation = "BUY"
                if price:
                    self.log(f'---Buy stop price: {price}')
                else:
                    self.log(f'---Buy price: {close_price}')
                return self.buy(size=amount, exectype=exectype, price=price)
            elif direction == "sell":
                self.last_operation = "SELL"
                if price:
                    self.log(f'---Sell stop price: {price}')
                else:
                    self.log(f'---Sell price: {close_price}')
                return self.sell(size=amount, exectype=exectype, price=price)
            elif direction == "close":
                self.last_operation = "CLOSE"
                return self.close(exectype=exectype, price=price, oco=oco)
            elif direction == "cancel":
                self.last_operation = "CANCEL"
                return self.cancel(ref)
        except Exception as e:
            self.log("ERROR: {}".format(sys.exc_info()[0]), color='red', send_telegram=True)
            self.log("{}".format(e), color='red', send_telegram=True)

    def notify_order(self, order):
        ticker = order.data._name
        self.log('{} Order {} Status {}'.format(
            ticker, order.ref, order.getstatusname())
        )

        # if not order.alive():  # not alive - nullify
        #     print('-- No longer alive self.orders[order.data]: {} '.format(self.orders[ticker]))





        if order.status in [order.Submitted]:
            # Buy/Sell order submitted to/by broker - Nothing to do
            if order.isbuy():
                self.log('BUY ORDER SUBMITTED')
            elif order.issell():
                self.log('SELL ORDER SUBMITTED')
            self.order = order
            return

        if order.status in [order.Accepted]:
            # Buy/Sell order accepted to/by broker - Nothing to do
            if order.isbuy():
                self.log('BUY ORDER ACCEPTED')
            elif order.issell():
                self.log('SELL ORDER ACCEPTED')
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED', True)

        elif order.status in [order.Completed]:
            if order.isbuy():
                if ENV == PRODUCTION and TRADING == "LIVE":
                    self.buy_price_close = float(order.ccxt_order['info']['avgPrice'])
                else:
                    self.buy_price_close = order.executed.price
                self.log_order(order, 'buy')
                if self.long_order and not self.long_stop_order:
                    self.sl_price = self.data0.low[0]*0.95
                    if 0.92*self.data0.open[0] > self.sl_price:
                        self.sl_price = 0.92*self.data0.open[0]
                    self.log(f'Placing Long Stop @ {self.sl_price}')
                    self.long_stop_order = self.exec_trade(direction="close", price=self.sl_price, exectype=bt.Order.Stop)
                if ENV == PRODUCTION:
                    print('order.__dict__')
                    print(order.__dict__)
                    print('order.executed.__dict__')
                    print(order.executed.__dict__)
                    print('order.ccxt_order')
                    print(order.ccxt_order)
                    print('order.ccxt_order[info]')
                    print(order.ccxt_order['info'])
                    print('order.ccxt_order[info].avgPrice')
                    print(order.ccxt_order['info']['avgPrice'])
                # self.log(
                #     'BUY EXECUTED, Price: %.2f, Cost (BTC): %.2f, Cost (USD): %.2f, Comm %.2f' %
                #     (order.executed.price,
                #      order.executed.value/order.executed.price,
                #      order.executed.value,
                #      order.executed.comm), True)
        
            elif order.issell():
                if ENV == PRODUCTION and TRADING == "LIVE":
                    self.sell_price_close = float(order.ccxt_order['info']['avgPrice'])
                else:
                    self.sell_price_close = order.executed.price
                self.log_order(order, 'sell')
                if self.short_order and not self.short_stop_order:
                    self.sl_price = self.highest_high_slow[0]
                    if 1.04*self.data0.open[0] < self.sl_price:
                        self.sl_price = 1.04*self.data0.open[0]
                    self.log(f'Placing Short Stop @ {self.sl_price}')
                    self.short_stop_order = self.exec_trade(direction="close", price=self.sl_price, exectype=bt.Order.Stop)
                if ENV == PRODUCTION:
                    print('order.__dict__')
                    print(order.__dict__)
                    print('order.executed.__dict__')
                    print(order.executed.__dict__)
                    print('order.ccxt_order')
                    print(order.ccxt_order)
                    print('order.ccxt_order[info]')
                    print(order.ccxt_order['info'])
                    print('order.ccxt_order[info].avgPrice')
                    print(order.ccxt_order['info']['avgPrice'])
                    # print(order.executed.__dict__)
                # self.log('SELL EXECUTED, Price: %.2f, Cost (BTC): %.2f, Cost (USD): %.2f, Comm %.2f' %
                #          (order.executed.price,
                #           order.executed.value/order.executed.price,
                #           order.executed.value,
                #           order.executed.comm), True)
        
        #     # Sentinel to None: new orders allowed
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if order.isbuy():
                self.log(f'BUY ORDER {order.Status[order.status]}')
            elif order.issell():
                self.log(f'SELL ORDER {order.Status[order.status]}')
            if order.status in [order.Margin, order.Rejected]:
                self.log_order(order, 'error')
            # self.log('Order Canceled/Margin/Rejected: Status %s - %s' % (order.Status[order.status],
            #                                                              self.last_operation), True)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.sl_price = None
        self.tp_price = None
        self.profit_percentage = None
        color = 'green'
        if trade.pnl < 0:
            color = 'red'
        # self.log(trade)
        self.log(colored('%s OPERATION PROFIT, GROSS %.2f, NET %.2f\n' % (trade.data._name, trade.pnl, trade.pnlcomm), color), True)

    def log_ohlc(self):
        self.log(f'''
        Open: {self.data0.open[0]}
        High: {self.data0.high[0]}
        Low: {self.data0.low[0]}
        Close: {self.data0.close[0]}''')

    # TODO - change order.executed.price to order.ccxt_order['info']['avgPrice'] for PRODUCTION
    def log_order(self, order, direction):
        if direction == "buy":
            price = self.buy_price_close
        elif direction == "sell":
            price = self.sell_price_close
        else:
            price = 0.0

        if ENV == PRODUCTION and TRADING == "LIVE":
            executed_size = order.ccxt_order['info']['executedQty']
        else:
            executed_size = order.executed.size

        color = ('red', 'green')[direction == 'buy']
        if direction == 'error':
            color = 'cyan'
        action = direction.capitalize()
        ticker = order.data._name
        self.log(f'''
        {action} {ticker}!
        {action} Price: {price}
        {action} Size: {executed_size}
        Open: {order.data.tick_open}
        High: {order.data.tick_high}
        Low: {order.data.tick_low}
        Close: {order.data.tick_close}
        Remaining size: {order.executed.remsize}
        PnL: {order.executed.pnl}
        ''', True, color)
        # Open: {self.data0.open[0]}
        # High: {self.data0.high[0]}
        # Low: {self.data0.low[0]}
        # Close: {self.data0.close[0]}
        # AttributeError: 'CCXTBroker' object has no attribute 'get_value'
        # Broker Value: {self.broker.get_value()}
        # Broker Cash: {self.broker.get_cash()} 
        # {action} Price * {action} Size: {order.executed.price * order.executed.size}
        # Current open position price: {order.executed.pprice}
        # Current open position size: {order.executed.psize}
        # Commission: {order.executed.comm}
        # Pclose: {order.executed.pclose}
        # Margin: {order.executed.margin}
        # Current Value: {order.executed.value}

    def log(self, txt, send_telegram=False, color=None, highlight=None, attrs=None):
        if not DEBUG:
            return
        # if ENV == DEVELOPMENT:
        #     return
        value = datetime.now()
        if len(self) > 0:
            value = self.data0.datetime.datetime()
        for_telegram = txt
        if color:
            txt = colored(txt, color, highlight, attrs)

        print('[%s] %s' % (value.strftime("%d-%m-%y %H:%M"), txt))
        if TRADING == "LIVE":
            send_telegram_message(for_telegram)
    
    def start(self):
        if ENV == PRODUCTION:
            if TRADING == "LIVE":
                # self.val_start = (self.broker.get_wallet_balance(BASE))[0]
                # self.log('BASE currency available: {} {}'.format(self.val_start, BASE), color='yellow')
                self.quote_available = (self.broker.get_wallet_balance(QUOTE))[0]
                self.log('QUOTE currency available: {} {}'.format(self.quote_available, QUOTE), color='yellow')
            else:
                self.val_start = self.broker.get_cash()
        else:
            self.val_start = self.broker.get_cash()

    def stop(self):
        # Calculate ROI
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('\nROI:        {:.2f}%'.format(100.0 * self.roi))

