import fnmatch
import pandas as pd
import os

MIN_HISTORY_AVAILABLE = 8760
datapath = '../fetch-historical-data'

tickers = []
def fetch_tickers():
    # Fetch all USDT tickers and append to tickers list
    # One week volume should be > $500,000
    ROLLING_VOLUME_PERIOD = 168
    # Minimum one year lookback for backtest
    MIN_HISTORY_AVAILABLE = 8760
    MIN_CUMULATIVE_VOLUME = 500000
    for file in os.listdir(datapath):
        if fnmatch.fnmatch(file, '*USDT-1h*.csv'):
            # TODO
            # If daily volume > $100,000, only then add to tickers
            ticker_ohlcv = pd.read_csv(f'../fetch-historical-data/{file}')
            cumulative_volume = 0
            if len(ticker_ohlcv) > MIN_HISTORY_AVAILABLE:
                # for i in range(ROLLING_VOLUME_PERIOD):
                    # cumulative_volume += ticker_ohlcv.values[i][5]
            # if cumulative_volume > MIN_CUMULATIVE_VOLUME:
                # Remove -1m.csv
                print(file)
                file = file[:-7]
                # Remove binance-
                file = file[8:]
                # Remove USDT
                # file = file[:-4]
                tickers.append(file)

    # print(tickers)
    return tickers


# tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT',
#            'ETCUSDT', 'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT',
#            'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT',
#            'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT', 'ALGOUSDT', 'ZILUSDT',
#            'KNCUSDT', 'ZRXUSDT', 'COMPUSDT', 'OMGUSDT', 'DOGEUSDT', 'KAVAUSDT',
#            'BANDUSDT', 'RLCUSDT', 'WAVESUSDT', 'MKRUSDT', 'SNXUSDT', 'DOTUSDT', 'YFIUSDT',
#            'BALUSDT', 'CRVUSDT', 'TRBUSDT', 'YFIIUSDT', 'RUNEUSDT', 'SUSHIUSDT', 'SRMUSDT',
#            'BZRXUSDT', 'EGLDUSDT', 'SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'BLZUSDT', 'UNIUSDT',
#            'AVAXUSDT', 'FTMUSDT', 'ENJUSDT', 'TOMOUSDT', 'RENUSDT',
#            'KSMUSDT', 'RSRUSDT', 'LRCUSDT']
def filter_tickers(tickers):
    new_tickers = []
    for ticker in tickers:
        ticker_ohlcv = pd.read_csv(f'../fetch-historical-data/binance-{ticker}-1h.csv')
        if len(ticker_ohlcv) > MIN_HISTORY_AVAILABLE*2:
            new_tickers.append(ticker)
    return new_tickers




# print(filter_tickers(tickers))
print(fetch_tickers())
