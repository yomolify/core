import fnmatch
import pandas as pd
import os

MIN_HISTORY_AVAILABLE = 8760
datapath = '../fetch-historical-data'

tickers = []
def fetch_tickers(quote):
    # Fetch all USDT tickers and append to tickers list
    # One week volume should be > $500,000
    ROLLING_VOLUME_PERIOD = 168
    # Minimum one year lookback for backtest
    MIN_HISTORY_AVAILABLE = 8760
    MIN_CUMULATIVE_VOLUME = 500000
    for file in os.listdir(datapath):
        if fnmatch.fnmatch(file, f'*{quote}-1h*.csv'):
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
        if len(ticker_ohlcv) > MIN_HISTORY_AVAILABLE:
            new_tickers.append(ticker)
    return new_tickers




# print(fetch_tickers('BTC'))

tickers = ['ENGBTC', 'CDTBTC', 'YOYOBTC', 'GOBTC', 'ETHBTC', 'RCNBTC', 'LINKBTC', 'XZCBTC', 'XRPBTC', 'MTLBTC',
             'HCBTC', 'ELFBTC', 'TNBBTC', 'DASHBTC', 'ENJBTC', 'BNBBTC', 'NEBLBTC', 'XVGBTC', 'HOTBTC', 'IOTXBTC',
             'SKYBTC', 'NAVBTC', 'BTSBTC', 'STORJBTC', 'QTUMBTC', 'PIVXBTC', 'BCDBTC', 'SNGLSBTC', 'XMRBTC', 'BQXBTC',
             'LTCBTC', 'GVTBTC', 'AIONBTC', 'IOSTBTC', 'SCBTC', 'QLCBTC', 'SNTBTC', 'ZRXBTC', 'ETCBTC', 'CVCBTC',
             'WABIBTC', 'KNCBTC', 'IOTABTC', 'ICXBTC', 'OAXBTC', 'BLZBTC', 'POEBTC', 'RLCBTC', 'QKCBTC', 'PPTBTC',
             'MCOBTC', 'ONTBTC', 'ZILBTC', 'ASTBTC', 'STORMBTC', 'THETABTC', 'SNMBTC', 'ZECBTC', 'INSBTC', 'BTGBTC',
             'ZENBTC', 'VIABTC', 'ARNBTC', 'WANBTC', 'RDNBTC', 'BRDBTC', 'XEMBTC', 'OMGBTC', 'CMTBTC', 'CNDBTC',
             'AMBBTC', 'BATBTC', 'ADXBTC', 'WPRBTC', 'VIBEBTC', 'DNTBTC', 'LUNBTC', 'ARKBTC', 'EDOBTC', 'AEBTC',
             'EVXBTC', 'LSKBTC', 'GXSBTC', 'FUELBTC', 'WTCBTC', 'STEEMBTC', 'REQBTC', 'BCPTBTC', 'OSTBTC', 'MTHBTC',
             'GTOBTC', 'VIBBTC', 'LENDBTC', 'POLYBTC', 'NXSBTC', 'POWRBTC', 'QSPBTC', 'VETBTC', 'ARDRBTC', 'KMDBTC',
             'RVNBTC', 'STRATBTC', 'NASBTC', 'APPCBTC', 'NULSBTC', 'TNTBTC', 'DOCKBTC', 'LOOMBTC', 'GRSBTC', 'ADABTC',
             'WAVESBTC', 'DLTBTC', 'BNTBTC', 'GASBTC', 'AGIBTC', 'TRXBTC', 'NCASHBTC', 'SYSBTC', 'DATABTC', 'GNTBTC',
             'NANOBTC', 'EOSBTC', 'POABTC', 'MDABTC', 'NEOBTC', 'REPBTC', 'DGDBTC', 'FUNBTC', 'MANABTC', 'LRCBTC',
             'XLMBTC']

print(filter_tickers(tickers))
