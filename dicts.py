import backtrader as bt
import datetime

from strategies import BuyHold, BollingerBands_template, RSI_EMA
from strategies.BollingerBands import L1, L2, L3, L4, L5, L6, L7, LS1, LS2

ExchangeCSVIndex = {
    'bitmex': {'open': 2, 'high': 3, 'low': 4, 'close': 5, 'volume': 7},
    'binance': {'open': 1, 'high': 2, 'low': 3, 'close': 4, 'volume': 5},
    'bitfinex': {'open': 1, 'high': 3, 'low': 4, 'close': 2, 'volume': 5}
    # 'bitfinex': {'open': 0, 'high': 2, 'low': 3, 'close': 1, 'volume': 4}
}

ExchangeDTFormat = {
    'bitmex': "%Y-%m-%d %H:%M:%S+00:00",
    'binance': '%Y-%m-%d %H:%M:%S',
    'bitfinex': lambda x: datetime.datetime.utcfromtimestamp(int(x[:-3]))
    # dtformat=('%b %d, %Y'),
}

Strategy = {
    'BollingerBands.L1': L1.L1,
    'BollingerBands.L2': L2.L2,
    'BollingerBands.L3': L3.L3,
    'BollingerBands.L4': L4.L4,
    'BollingerBands.L5': L5.L5,
    'BollingerBands.L6': L6.L6,
    'BollingerBands.L7': L7.L7,
    'BollingerBands.LS1': LS1.LS1,
    'BollingerBands.LS2': LS2.LS2,
    'RSI_EMA': RSI_EMA.RSA_EMA,
    'BuyHold.BuyAndHold_Buy': BuyHold.BuyAndHold_Buy,
    'BuyHold.BuyAndHold_Target': BuyHold.BuyAndHold_Target,
    'BuyHold.BuyAndHold_Target': BuyHold.BuyAndHold_Target,
    'BuyHold.BuyAndHold_More': BuyHold.BuyAndHold_More,
    'BuyHold.BuyAndHold_More_Fund': BuyHold.BuyAndHold_More_Fund,
}

ExecType = {
    'Limit': bt.Order.Limit,
    'Market': bt.Order.Market,
}