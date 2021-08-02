import backtrader as bt
import sys
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, TRADING
import datetime as dt


class TestSMA(StrategyBase):
    params = (
        ('exectype', bt.Order.Market),
        ('period_sma_bitcoin', 1),
        ('order_target_percent', 4)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.i = 0
        self.bitcoin = self.datas[0]
        self.altcoins = self.datas
        self.placed_orders = None
        self.last_len = {}
        self.inds = {}
        self.orders = dict()
        for d in self.datas:
            self.last_len[d] = 0
        self.bitcoin_atr = bt.indicators.AverageTrueRange(self.bitcoin)
        self.bitcoin_sma = bt.indicators.SimpleMovingAverage(self.bitcoin.close - self.bitcoin_atr,
                                                             period=self.params.period_sma_bitcoin)

    def next(self):
        if self.status == "LIVE":
            # available = list(filter(lambda d: len(d) > 1, self.altcoins))
            # allowed = True
            # for i, d in enumerate(self.altcoins):
            #     if len(d) <= self.last_len[d]:
            #         allowed = False
            #     else:
            #         self.last_len[d] = len(d)

            # if allowed:
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
                # if current_position > 0:
                #     try:
                #         order = self.add_order(data=d, target=0, type='market')
                #         print('current_position > 0')
                #     except Exception as e:
                #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                #         self.log("{}".format(e))
                # elif current_position < 0:
                #     try:
                #         order = self.add_order(data=d, target=0, type="market")
                #         print('current_position < 0')
                #     except Exception as e:
                #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                #         self.log("{}".format(e))
                if current_position == 0:
                    if True or self.bitcoin.close[0] > self.bitcoin_sma[0]:
                        try:
                            if (ticker in self.orders) and (self.orders[ticker] is not None):
                                self.cancel(self.orders[ticker])
                                self.orders[ticker] = None
                            self.add_order(data=d, price=d.close[0] - 100 * (d.high[0] - d.low[0]), target=(self.p.order_target_percent / 100), type="limit")
                            # self.orders[ticker] = self.buy(d, size=0.001, price=d.close[0] + 1000, exectype=bt.Order.Stop)
                            print('placing order sma >')
                        except Exception as e:
                            self.log("ERROR: {}".format(sys.exc_info()[0]))
                            self.log("{}".format(e))

                    # elif self.bitcoin.close[0] < self.bitcoin_sma[0]:
                    #     try:
                    #         self.orders[ticker] = [self.add_order(data=d, target=-(self.p.order_target_percent/100), type="market")]
                    #         print('placing order sma <')
                    #     except Exception as e:
                    #         self.log("ERROR: {}".format(sys.exc_info()[0]))
                    #         self.log("{}".format(e))



            if self.to_place_orders is not None and len(self.to_place_orders) > 0:
                print(self.to_place_orders)
                order_chunks = [self.to_place_orders[x:x + 5] for x in range(0, len(self.to_place_orders), 5)]
                for order_chunk in order_chunks:
                    self.placed_orders = self.place_batch_order(order_chunk)

            for i, d in enumerate(self.altcoins):
                ticker = d._name
                for placed_order in self.placed_orders:
                    if placed_order.ccxt_order["symbol"] == ticker:
                        # Only remember the most recently placed order for a ticker, TODO: improve soon
                        self.orders[ticker] = placed_order
