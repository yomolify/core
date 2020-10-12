import sys
from datetime import datetime, timedelta
import backtrader as bt
from termcolor import colored
from config import DEVELOPMENT, BASE, QUOTE, ENV, PRODUCTION, DEBUG, TRADING
from utils import send_telegram_message

# TODO implement isPosition
LONG = "LONG"


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
        color = ('red', 'green')[direction == 'buy']
        close_price = self.data0.close[0]
        # self.log(f'{direction.capitalize()} supplied price is {price}')
        if ENV != PRODUCTION:
            # self.log("{} ordered @ ${}".format(direction.capitalize(), close_price))
            amount = size

        if ENV == PRODUCTION:
            self.log('{}'.format(self.position), color='magenta', send_telegram=True)
            # self.log('Data time: {}, Computer Time: {}'.format(self.data0.datetime.datetime(), datetime.now() - timedelta(minutes=63)))
            if self.data0.datetime.datetime() < datetime.now() - timedelta(minutes=63):
                self.log('Historical data, so not placing real order')
                return
            # BUY/SELL BASE coin for QUOTE
            target = (BASE, QUOTE)[direction == 'buy']
            if TRADING == "LIVE":
                cash, value = self.broker.get_wallet_balance(target)
                self.log('{} available: {}'.format(target, cash), color='yellow')
            else:
                cash = self.broker.get_cash()
                value = self.broker.get_value()

            if size is None:
                amount = ((cash, cash / close_price)[direction == 'buy']) * 0.99
            else:
                amount = size

            # Hack for correct logs while paper trading
            if TRADING == "PAPER":
                if direction != "buy":
                    amount = self.position.size
            self.log('''
                %sing %.2f %s for %.2f %s!
                close_Price: $%.2f
                Amount: %.2f %s
                Cost: %.2f %s
                Balance: $%.2f USDT'''
                     % (direction.capitalize(), amount, BASE, close_price * amount, QUOTE, close_price, amount, BASE,
                        close_price * amount, QUOTE, cash), True, color)
        try:
            if direction == "buy":
                self.last_operation = "BUY"
                if price:
                    self.log(f'---Buy stop price: {price}')
                return self.buy(size=amount, exectype=exectype, price=price)
            elif direction == "sell":
                self.last_operation = "SELL"
                if price:
                    self.log(f'---Sell stop price: {price}')
                return self.sell(size=amount, exectype=exectype, price=price)
            elif direction == "close":
                self.last_operation = "CLOSE"
                if exectype == bt.Order.Stop:
                    self.log(f'Stop Order @ {price}')
                return self.close(exectype=exectype, price=price, oco=oco)
            elif direction == "cancel":
                self.last_operation = "CANCEL"
                return self.cancel(ref)
        except Exception as e:
            self.log("ERROR: {}".format(sys.exc_info()[0]), color='red')
            self.log("{}".format(e), color='red')

    def notify_order(self, order):
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
                self.log(f'BUY ORDER ACCEPTED @ {self.data0.open[0]}')
            elif order.issell():
                self.log(f'SELL ORDER ACCEPTED @ {self.data0.open[0]}')
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED', True)

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price_close = order.executed.price
                # self.log(f'Executed BUY price: {self.buy_price_close}')
                self.log_order(order, 'buy')
                if self.long_order and not self.long_stop_order and not self.stop_loss_slow_sma:
                    self.sl_price = self.data0.low[0] * 0.95
                    # 8% emergency stop
                    if 0.92 * self.data0.open[0] > self.sl_price:
                        self.sl_price = 0.92 * self.data0.open[0]
                    self.log(f'Placing Long Stop @ {self.sl_price}')
                    self.long_stop_order = self.exec_trade(direction="close", price=self.sl_price,
                                                           exectype=bt.Order.Stop)
                # if self.long_order and not self.long_stop_order and self.stop_loss_slow_sma:
                #     self.log(f'Placing Long Stop for veryslow @ {self.sl_price}')
                #     self.long_stop_order = self.exec_trade(direction="close", price=self.sl_price, exectype=bt.Order.Stop)

                # self.last_operation = "BUY"
                if ENV == PRODUCTION:
                    print(order.__dict__)
                    # print(order.executed.__dict__)
                # self.log(
                #     'BUY EXECUTED, Price: %.2f, Cost (BTC): %.2f, Cost (USD): %.2f, Comm %.2f' %
                #     (order.executed.price,
                #      order.executed.value/order.executed.price,
                #      order.executed.value,
                #      order.executed.comm), True)

            elif order.issell():
                self.sell_price_close = order.executed.price
                # self.log(f'Executed SELL price: {self.sell_price_close}')
                self.log_order(order, "sell")
            # self.log(f'self.short_order: {self.short_order}')
            # self.log(f'self.short_stop_order: {self.short_stop_order}')
            if self.short_order and not self.short_stop_order:
                self.sl_price = self.highest_high_slow[0]
                # 4% emergency stop
                if 1.04 * self.data0.open[0] < self.sl_price:
                    self.sl_price = 1.04 * self.data0.open[0]
                    self.log(f'Placing Short Stop @ {self.sl_price}')
                    self.short_stop_order = self.exec_trade(direction="close", price=self.sl_price,
                                                            exectype=bt.Order.Stop)
                # self.last_operation = "SELL"
                # self.reset_sell_indicators()
                if ENV == PRODUCTION:
                    print(order.__dict__)
                    # print(order.executed.__dict__)
                # self.log('SELL EXECUTED, Price: %.2f, Cost (BTC): %.2f, Cost (USD): %.2f, Comm %.2f' %
                #          (order.executed.price,
                #           order.executed.value/order.executed.price,
                #           order.executed.value,
                #           order.executed.comm), True)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if order.isbuy():
                self.log(f'BUY ORDER {order.Status[order.status]}')
                # self.log(order)
            elif order.issell():
                self.log(f'SELL ORDER {order.Status[order.status]}')
            if order.status in [order.Margin, order.Rejected]:
                self.log_order(order, 'error')
        # Sentinel to None: new orders allowed
        self.order = None

    def log_ohlc(self):
        self.log(f'''
        Open: {self.data0.open[0]}
        High: {self.data0.high[0]}
        Low: {self.data0.low[0]}
        Close: {self.data0.close[0]}''')

    def log_order(self, order, direction):
        color = ('red', 'green')[direction == 'buy']
        if direction == 'error':
            color = 'cyan'
        action = direction.capitalize()
        self.log(f'''
        {action}!
        Open: {self.data0.open[0]}
        High: {self.data0.high[0]}
        Low: {self.data0.low[0]}
        Close: {self.data0.close[0]}
        {action} Price: {order.executed.price}
        {action} Size: {order.executed.size}
        {action} Price * {action} Size: {order.executed.price * order.executed.size}
        Current open position price: {order.executed.pprice}
        Current open position size: {order.executed.psize}
        Remaining size: {order.executed.remsize}
        Current Value: {order.executed.value}
        Broker Value: {self.broker.get_value()}
        Broker Cash: {self.broker.get_cash()} 
        PnL: {order.executed.pnl}
        Margin: {order.executed.margin}
        Commission: {order.executed.comm}
        Pclose: {order.executed.pclose}
        ''', True, color)

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
        self.log(colored('OPERATION PROFIT, GROSS %.2f, NET %.2f\n' % (trade.pnl, trade.pnlcomm), color), True)

    def log(self, txt, send_telegram=False, color=None, highlight=None, attrs=None):
        if not DEBUG:
            return
        # if ENV == DEVELOPMENT:
        #     return
        value = datetime.now()
        if len(self) > 0:
            value = self.data0.datetime.datetime()

        if color:
            txt = colored(txt, color, highlight, attrs)

        print('[%s] %s' % (value.strftime("%d-%m-%y %H:%M"), txt))
        if TRADING == "LIVE" and send_telegram:
            send_telegram_message(txt)

    def start(self):
        if ENV == PRODUCTION:
            if TRADING == "LIVE":
                self.val_start = (self.broker.get_wallet_balance(BASE))[0]
                self.log('BASE currency available: {} {}'.format(self.val_start, BASE), color='yellow')
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
