from datetime import datetime
import backtrader as bt
from termcolor import colored
from config import DEVELOPMENT, COIN_TARGET, COIN_REFER, ENV, PRODUCTION, DEBUG
from utils import send_telegram_message

class StrategyBase(bt.Strategy):
    def __init__(self):
        self.sl_price = 0
        self.tp_price = 0
        self.order = None
        self.last_operation = "SELL"
        self.status = "DISCONNECTED"
        self.bar_executed = 0
        self.buy_price_close = None
        self.log("Base strategy initialized")

    def reset_sell_indicators(self):
        self.buy_price_close = None

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        print(self.status)
        if status == data.LIVE:
            self.log("LIVE DATA - Ready to trade")

    def exec_trade(self, direction, exectype):
        # self.log("%s ordered: $%.2f" % direction, self.data0.close[0], True)
        self.log("{} ordered @ ${}".format(direction.capitalize(), self.data0.close[0]))
        price = self.data0.close[0]
        
        if ENV == PRODUCTION:
            cash, value = self.broker.get_wallet_balance(COIN_REFER)
            amount = (value / price) * 0.99  # Workaround to avoid precision issues
            self.log("%s ordered: $%.2f. Amount %.6f %s. Balance $%.2f USDT" % (direction, self.data0.close[0],
                                                                              amount, COIN_TARGET, value), True)
        if direction == "buy":
            if ENV == DEVELOPMENT:
                return self.buy(exectype=exectype)
            return self.buy(size=amount, exectype=exectype)
        elif direction == "sell":
            if ENV == DEVELOPMENT:
                return self.sell(exectype=exectype)
            return self.sell(size=amount, exectype=exectype)
        elif direction == "close":
            if ENV == DEVELOPMENT:
                return self.close(exectype=exectype)
            return self.close(size=amount, exectype=exectype)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED/SUBMITTED')
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

    def log(self, txt, send_telegram=False, color=None):
        if not DEBUG:
            return
        # Uncomment for detailed logs
        # return
        value = datetime.now()
        if len(self) > 0:
            value = self.data0.datetime.datetime()

        if color:
            txt = colored(txt, color)

        print('[%s] %s' % (value.strftime("%d-%m-%y %H:%M"), txt))
        if send_telegram:
            send_telegram_message(txt)
