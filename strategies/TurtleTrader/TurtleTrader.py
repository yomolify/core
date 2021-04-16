import backtrader as bt
import backtrader_addons as bta
import datetime
from strategies.base import StrategyBase


class TurtleTrader(StrategyBase):

    params = (
        ('exectype', bt.Order.Market),
        ('period_s1_entry', 20),
        ('period_s1_exit', 10),
        ('period_s2_entry', 55),
        ('period_s2_exit', 20),
        ('period_atr', 20),
        ('percent_risk', 0.02),
        ('order_target_percent', 0.02),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.indicators = {}
        self.orders = dict()

        for d in self.datas:
            ticker = d._name
            self.indicators[ticker] = {}
            self.indicators[ticker]["s1_long_entry"] = bt.indicators.Highest(d.high, period=self.params.period_s1_entry, plot=True, subplot=False)
            self.indicators[ticker]["s1_long_exit"] = bt.indicators.Lowest(d.low, period=self.params.period_s1_exit, plot=True, subplot=False)
            self.indicators[ticker]["s2_long_entry"] = bt.indicators.Lowest(d.low, period=self.params.period_s2_entry, plot=True, subplot=False)
            self.indicators[ticker]["s2_long_exit"] = bt.indicators.Lowest(d.low, period=self.params.period_s2_exit, plot=True, subplot=False)
            self.indicators[ticker]["s1_short_entry"] = bt.indicators.Lowest(d.high, period=self.params.period_s1_entry,
                                                                             plot=True, subplot=False)
            self.indicators[ticker]["s1_short_exit"] = bt.indicators.Highest(d.low, period=self.params.period_s1_exit,
                                                                           plot=True, subplot=False)
            self.indicators[ticker]["s2_short_entry"] = bt.indicators.Lowest(d.low, period=self.params.period_s2_entry,
                                                                            plot=True, subplot=False)
            self.indicators[ticker]["s2_short_exit"] = bt.indicators.Highest(d.low, period=self.params.period_s2_exit,
                                                                           plot=True, subplot=False)
            self.indicators[ticker]["average_true_range"] = bt.indicators.ATR(d, period=self.params.period_atr)

    def next(self):
        # TODO - Filter trades that where previous breakout was a success in S1 they should be only taken if S2 hits
        # Position size = 2 percent of portfolio value / 2*ATR  

        available = list(filter(lambda d: len(d), self.datas))
        for i, d in enumerate(available):
            ticker = d._name
            current_position = self.getposition(d).size
            # self.log('{} Position {}'.format(ticker, current_position))
            if current_position > 0:
                # LONG EXIT S1 & S2
                if (d.close[0] < self.indicators[ticker]['s1_long_exit'][-1]) or (d.close[0] < self.indicators[ticker]['s2_long_exit'][-1]):
                    order = self.order_target_percent(data=d, target=0)
                    self.orders[ticker].append(order)
            elif current_position < 0:
                # SHORT EXIT S1 & S2
                if (d.high[0] > self.indicators[ticker]['s1_short_exit'][-1]) or (d.high[0] > self.indicators[ticker]['s2_short_exit'][-1]):
                    order = self.order_target_percent(data=d, target=0)
                    self.orders[ticker].append(order)
            if current_position == 0:
                # LONG ENTRY S1 & S2
                if (d.close[0] > self.indicators[ticker]['s1_long_entry'][-1]) or (d.high[0] > self.indicators[ticker]['s2_long_entry'][-1]):
                    percent_risk = self.broker.get_value() * self.p.percent_risk
                    atr = self.indicators[ticker]['average_true_range'][0]
                    size = percent_risk / (2 * atr)
                    dollar_value = (size * d.close[0])
                    target_percent = (self.p.percent_risk / (2*atr))*10
                    # self.orders[ticker] = [self.order_target_percent(data=d, target=self.p.order_target_percent)]
                    self.orders[ticker] = [self.order_target_value(data=d, target=dollar_value)]
                    # self.orders[ticker] = [self.order_target_percent(data=d, target=target_percent)]
                    # self.log('{} Buy initiated {}'.format(ticker, self.orders[ticker][0]))
                # SHORT ENTRY S1 & S2
                elif (d.low[0] < self.indicators[ticker]['s1_short_entry'][-1]) or (d.low[0] < self.indicators[ticker]['s2_short_entry'][-1]):
                    percent_risk = self.broker.get_value() * self.p.percent_risk
                    atr = self.indicators[ticker]['average_true_range'][0]
                    size = percent_risk / (2 * atr)
                    dollar_value = (size * d.close[0])
                    target_percent = (self.p.percent_risk / (2*atr)) * 10
                    # self.orders[ticker] = [self.order_target_percent(data=d, target=-self.p.order_target_percent)]
                    self.orders[ticker] = [self.order_target_value(data=d, target=-dollar_value)]
                    # self.orders[ticker] = [self.order_target_percent(data=d, target=-target_percent)]
                    # self.log('{} Sell initiated {}'.format(ticker, self.orders[ticker][0]))
