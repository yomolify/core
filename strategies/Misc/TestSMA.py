import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING
import datetime as dt

class TestSMA(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_sma_bitcoin', 1),
        ('order_target_percent', 1)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.inds = {}
        self.orders = dict()
        self.bitcoin_atr = bt.indicators.AverageTrueRange(self.bitcoin)
        self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close-self.bitcoin_atr,
                                                            period=self.params.period_sma_bitcoin)

    def next(self):
        if self.status == "LIVE":
            # available = list(filter(lambda d: len(d) > 1, self.altcoins))
            for i, d in enumerate(self.altcoins):
                ticker = d._name
                print(dt.datetime.now())
                print(f'{ticker}')
                current_position = 0
                position = self.getposition(d)
                print(position)
                if position is not None:
                    current_position = self.getposition(d)["size"]
                if current_position:
                    print(f'{ticker} position is: {current_position}')
                if current_position > 0:
                    try:
                        order = self.add_order(data=d, target=0, type='market')
                        print('current_position > 0')
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                elif current_position < 0:
                    try:
                        order = self.add_order(data=d, target=0, type="market")
                        print('current_position < 0')
                    except Exception as e:
                        self.log("ERROR: {}".format(sys.exc_info()[0]))
                        self.log("{}".format(e))
                if current_position == 0:
                    if self.bitcoin.close[0] > self.bitcoin_sma[0]:
                        try:
                            self.orders[ticker] = [self.add_order(data=d, target=((self.p.order_target_percent/100)), type="market")]
                            print('placing order sma >')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))

                    elif self.bitcoin.close[0] < self.bitcoin_sma[0]:
                        try:
                            self.orders[ticker] = [self.add_order(data=d, target=-(self.p.order_target_percent/100), type="market")]
                            print('placing order sma <')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))
            if len(self.to_place_orders) > 0:
                print(self.to_place_orders)
                self.place_batch_order(self.to_place_orders)