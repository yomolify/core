datapath = '../fetch-historical-data'
tickers = []
# All tickers with 7 day vollume > $500000 and minimum one year historical data
tickers = ['BTC', 'ETH', 'IOST', 'XLM', 'BEAM', 'BAND', 'DUSK', 'CVC', 'BAT', 'TRX', 'TFUEL', 'ONG', 'THETA', 'ADA',
           'KEY', 'WAVES',
           'MTL', 'IOTA', 'TOMO', 'ICX', 'ONT', 'WIN', 'ENJ', 'XRP', 'OMG', 'FET', 'BNB', 'ONE', 'MFT', 'XTZ',
           'ZIL', 'BTT', 'ATOM', 'NANO', 'EOS', 'HOT', 'REN', 'NPXS', 'ALGO', 'FUN', 'ZRX', 'MITH', 'PERL',
           'GTO', 'LINK', 'RVN', 'COS', 'ANKR', 'COCOS', 'QTUM', 'DOCK', 'NULS', 'NKN', 'PAX', 'ERD',
           'FTM', 'DOGE', 'MATIC', 'CELR', 'VET', 'HBAR', 'CHZ', 'WAN', 'ETC', 'DENT']

# Stablecoins from above list
# 'TUSD', 'USDS', 'BUSD', 'USDC',

# All tickers with 7 day vollume > 500000 and minimum 7 days historical data
tickers = ['IOST', 'WNXM', 'XLM', 'BTS', 'RUNE', 'VTHO', 'BEAM', 'SAND', 'LRC', 'NEAR', 'BKRW', 'EOSBEAR', 'BNBBULL',
           'JST', 'GBP', 'EUR', 'BAND', 'DUSK', 'LUNA', 'CVC', 'BAT', 'TRX', 'STPT', 'TFUEL', 'OXT', 'ONG', 'THETA',
           'ADA', 'PNT', 'MBL', 'XTZDOWN', 'UNI', 'TROY', 'ARDR', 'XVS', 'BTCUP', 'KEY', 'WAVES', 'MTL', 'IOTA', 'TOMO',
           'BCHSV', 'DREP', 'ICX', 'HNT', 'FLM', 'ONT', 'FIO', 'CTSI', 'IOTX', 'BNT', 'BEL', 'WIN', 'VEN', 'ENJ',
           'STRAT',
           'NBS', 'XRP', 'CRV', 'DGB', 'USDS', 'SNX', 'OMG', 'UTK', 'DIA', 'FET', 'STMX', 'AION', 'OCEAN', 'STX', 'BNB',
           'COTI', 'ONE', 'SXP', 'MFT', 'UNIUP', 'XTZ', 'WING', 'UMA', 'ZIL', 'AAVE', 'BTT', 'TCT', 'ATOM', 'KNC',
           'NANO',
           'BLZ', 'KMD', 'SUSHI', 'MCO', 'EOS', 'RLC', 'HOT', 'REN', 'NPXS', 'ANT', 'SOL', 'ETHBEAR', 'ALGO', 'FUN',
           'BUSD', 'ZRX', 'LSK', 'MITH', 'STORJ', 'LINKDOWN', 'KAVA', 'WTC', 'PERL', 'USDC', 'HIVE', 'GTO', 'LEND',
           'LINK', 'RVN', 'COS', 'FIL', 'ANKR', 'OGN', 'COCOS', 'IRIS', 'MANA', 'FTT', 'MDT', 'QTUM', 'DOCK', 'TUSD',
           'TRB', 'AVAX', 'NULS', 'NKN', 'DOTDOWN', 'PAX', 'GXS', 'DATA', 'ERD', 'FTM', 'DOGE', 'SC', 'EGLD', 'MATIC',
           'CELR', 'BTCDOWN', 'DOT', 'VET', 'ORN', 'DAI', 'RSR', 'XTZUP', 'HBAR', 'CHZ', 'SRM', 'STORM', 'ARPA',
           'LINKUP',
           'VITE', 'WRX', 'WAN', 'BZRX', 'ETC', 'LTO', 'DENT', 'AUD', 'CTXC', 'SUN', 'ALPHA', 'CHR']

# FUTURES
# Best returns with NewYearlyHighs
tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT',
           'ETCUSDT', 'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT',
           'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT',
           'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT', 'ALGOUSDT', 'ZILUSDT']

# All FUTURES
tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT',
           'ETCUSDT', 'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT',
           'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT',
           'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT', 'ALGOUSDT', 'ZILUSDT',
           'KNCUSDT', 'ZRXUSDT', 'COMPUSDT', 'OMGUSDT', 'DOGEUSDT', 'KAVAUSDT',
           'BANDUSDT', 'RLCUSDT', 'WAVESUSDT', 'MKRUSDT', 'SNXUSDT', 'DOTUSDT', 'YFIUSDT',
           'BALUSDT', 'CRVUSDT', 'TRBUSDT', 'YFIIUSDT', 'RUNEUSDT', 'SUSHIUSDT', 'SRMUSDT',
           'BZRXUSDT', 'EGLDUSDT', 'SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'BLZUSDT', 'UNIUSDT',
           'AVAXUSDT', 'FTMUSDT', 'ENJUSDT', 'TOMOUSDT', 'RENUSDT',
           'KSMUSDT', 'RSRUSDT', 'LRCUSDT', 'BCHUSDT', 'SXPUSDT']

# Futures with atleast one year of historical data
tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT', 'ETCUSDT', 'LINKUSDT', 'XLMUSDT',
           'ADAUSDT',
           'XMRUSDT', 'DASHUSDT', 'ZECUSDT', 'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT',
           'VETUSDT',
           'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT', 'ALGOUSDT', 'ZILUSDT', 'ZRXUSDT', 'OMGUSDT', 'DOGEUSDT',
           'BANDUSDT', 'WAVESUSDT', 'ICXUSDT', 'FTMUSDT', 'ENJUSDT', 'TOMOUSDT', 'RENUSDT']

# Futures with atleast two years of historical data
tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT', 'ETCUSDT', 'XLMUSDT', 'ADAUSDT', 'BNBUSDT',
           'ONTUSDT', 'IOTAUSDT', 'VETUSDT', 'NEOUSDT', 'QTUMUSDT', 'ICXUSDT']
