datapath = '../fetch-historical-data'
tickers = []

tickers = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT', 'ETCUSDT', 'LINKUSDT', 'XLMUSDT',
           'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT', 'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT',
           'BATUSDT', 'VETUSDT', 'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT', 'ALGOUSDT', 'ZILUSDT', 'KNCUSDT',
           'ZRXUSDT', 'COMPUSDT', 'OMGUSDT', 'DOGEUSDT', 'KAVAUSDT', 'BANDUSDT', 'RLCUSDT', 'WAVESUSDT', 'MKRUSDT',
           'SNXUSDT', 'DOTUSDT', 'YFIUSDT', 'BALUSDT', 'CRVUSDT', 'TRBUSDT', 'YFIIUSDT', 'RUNEUSDT', 'SUSHIUSDT',
           'SRMUSDT', 'BZRXUSDT', 'EGLDUSDT', 'SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'BLZUSDT', 'UNIUSDT', 'AVAXUSDT',
           'FTMUSDT', 'ENJUSDT', 'TOMOUSDT', 'RENUSDT', 'KSMUSDT', 'RSRUSDT', 'LRCUSDT', 'IOST', 'XLM', 'BEAM', 'ZEC',
           'XMR', 'BAND', 'DUSK', 'CVC', 'BAT', 'TRX', 'TFUEL', 'ONG', 'THETA', 'ADA', 'KEY', 'WAVES', 'MTL', 'IOTA',
           'TOMO', 'ICX', 'ETH', 'ONT', 'LTC', 'WIN', 'ENJ', 'HC', 'XRP', 'BCC', 'USDS', 'OMG', 'FET', 'BNB', 'ONE',
           'MFT', 'XTZ', 'ZIL', 'BTT', 'ATOM', 'NANO', 'EOS', 'HOT', 'REN', 'NPXS', 'ALGO', 'FUN', 'BUSD', 'ZRX',
           'MITH', 'PERL', 'USDC', 'GTO', 'LINK', 'RVN', 'COS', 'ANKR', 'COCOS', 'DASH', 'QTUM', 'DOCK', 'TUSD', 'NULS',
           'NKN', 'PAX', 'ERD', 'FTM', 'DOGE', 'MATIC', 'CELR', 'VET', 'HBAR', 'CHZ', 'WAN', 'ETC', 'BTC', 'DENT',
           'BCHABC', 'NEO']

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

# All spot altcoins with > one year historical data, stablecoins and badcoins removed
tickers = ['BTCUSDT', 'IOSTUSDT', 'XLMUSDT', 'BEAMUSDT', 'ZECUSDT', 'XMRUSDT', 'BANDUSDT', 'DUSKUSDT', 'CVCUSDT',
           'BATUSDT',
           'TRXUSDT', 'TFUELUSDT', 'ONGUSDT', 'THETAUSDT', 'ADAUSDT', 'KEYUSDT', 'WAVESUSDT', 'MTLUSDT', 'IOTAUSDT',
           'TOMOUSDT', 'ICXUSDT', 'ONTUSDT', 'LTCUSDT', 'WINUSDT', 'ENJUSDT', 'HCUSDT', 'XRPUSDT',
           'OMGUSDT', 'FETUSDT', 'BNBUSDT', 'ONEUSDT', 'MFTUSDT', 'XTZUSDT', 'ZILUSDT', 'BTTUSDT', 'ATOMUSDT',
           'ETHUSDT',
           'NANOUSDT', 'EOSUSDT', 'HOTUSDT', 'RENUSDT', 'NPXSUSDT', 'ALGOUSDT', 'FUNUSDT', 'ZRXUSDT',
           'MITHUSDT', 'PERLUSDT', 'GTOUSDT', 'LINKUSDT',
           'RVNUSDT', 'COSUSDT', 'ANKRUSDT', 'COCOSUSDT',
           'DASHUSDT', 'QTUMUSDT', 'DOCKUSDT', 'NULSUSDT',
           'NKNUSDT', 'PAXUSDT', 'ERDUSDT', 'FTMUSDT',
           'DOGEUSDT', 'MATICUSDT', 'CELRUSDT', 'VETUSDT',
           'HBARUSDT', 'CHZUSDT', 'WANUSDT', 'ETCUSDT',
           'DENTUSDT', 'NEOUSDT']

# 'BCHABCUSDT', 'BCCUSDT','BUSDUSDT', 'USDCUSDT', 'USDSUSDT', 'TUSDUSDT',
# All BTC pairs
tickers = ['DUSKBTC', 'ENGBTC', 'CDTBTC', 'YOYOBTC', 'GOBTC', 'ETHBTC', 'RCNBTC', 'LINKBTC', 'XZCBTC',
           'XRPBTC', 'MTLBTC', 'HCBTC', 'ELFBTC', 'TNBBTC', 'DASHBTC', 'HBARBTC', 'ENJBTC', 'BNBBTC',
           'NEBLBTC', 'XVGBTC', 'TOMOBTC', 'HOTBTC', 'IOTXBTC', 'SKYBTC', 'KEYBTC', 'NAVBTC', 'BTSBTC',
           'STORJBTC', 'QTUMBTC', 'PIVXBTC', 'BCDBTC', 'SNGLSBTC', 'XMRBTC', 'BQXBTC', 'LTCBTC', 'GVTBTC',
           'ATOMBTC', 'AIONBTC', 'IOSTBTC', 'SCBTC', 'QLCBTC', 'SNTBTC', 'ZRXBTC', 'ETCBTC', 'CVCBTC',
           'WABIBTC', 'KNCBTC', 'IOTABTC', 'ICXBTC', 'BCCBTC', 'OAXBTC', 'BLZBTC', 'POEBTC', 'RLCBTC',
           'QKCBTC', 'PPTBTC', 'MCOBTC', 'ONTBTC', 'ZILBTC', 'ASTBTC', 'STORMBTC', 'THETABTC', 'NKNBTC',
           'PHBBTC', 'ALGOBTC', 'SNMBTC', 'ZECBTC', 'INSBTC', 'ONGBTC', 'CHZBTC', 'BTGBTC', 'MITHBTC',
           'ZENBTC', 'VIABTC', 'ARNBTC', 'WANBTC', 'RDNBTC', 'BRDBTC', 'XEMBTC', 'OMGBTC', 'CMTBTC',
           'DOGEBTC', 'CNDBTC', 'AMBBTC', 'SALTBTC', 'ERDBTC', 'BANDBTC', 'BATBTC', 'ADXBTC', 'FETBTC',
           'WPRBTC', 'VIBEBTC', 'DNTBTC', 'NPXSBTC', 'LUNBTC', 'FTMBTC', 'ARKBTC', 'EDOBTC', 'AEBTC',
           'EVXBTC', 'COSBTC', 'LSKBTC', 'CELRBTC', 'DCRBTC', 'GXSBTC', 'FUELBTC', 'BCHABCBTC', 'MFTBTC',
           'WTCBTC', 'STEEMBTC', 'REQBTC', 'BCPTBTC', 'XTZBTC', 'OSTBTC', 'MTHBTC', 'GTOBTC', 'VIBBTC',
           'LENDBTC', 'POLYBTC', 'NXSBTC', 'POWRBTC', 'QSPBTC', 'VETBTC', 'ARDRBTC', 'KMDBTC', 'MODBTC',
           'RVNBTC', 'DENTBTC', 'STRATBTC', 'SUBBTC', 'NASBTC', 'APPCBTC', 'NULSBTC', 'TNTBTC', 'DOCKBTC',
           'LOOMBTC', 'MATICBTC', 'GRSBTC', 'ADABTC', 'WAVESBTC', 'DLTBTC', 'BNTBTC', 'GASBTC', 'AGIBTC',
           'TRXBTC', 'NCASHBTC', 'PERLBTC', 'SYSBTC', 'RENBTC', 'DATABTC', 'GNTBTC', 'NANOBTC', 'ONEBTC',
           'EOSBTC', 'TFUELBTC', 'ANKRBTC', 'POABTC', 'MDABTC', 'BEAMBTC', 'NEOBTC', 'REPBTC', 'DGDBTC',
           'FUNBTC', 'MANABTC', 'LRCBTC', 'XLMBTC', 'WINGSBTC']

# BTC pairs with atleast two years historical data
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
# All Futures
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

# All futures with listing before 1st October 2020
tickers = ['ADA/USDT', 'ALGO/USDT', 'ATOM/USDT', 'AVAX/USDT', 'BAL/USDT', 'BAND/USDT', 'BAT/USDT', 'BCH/USDT',
                   'BLZ/USDT', 'BNB/USDT', 'BTC/USDT', 'BZRX/USDT', 'COMP/USDT', 'CRV/USDT', 'DASH/USDT', 'DOGE/USDT',
                   'DOT/USDT', 'EGLD/USDT', 'ENJ/USDT', 'EOS/USDT', 'ETC/USDT', 'ETH/USDT', 'FLM/USDT', 'FTM/USDT',
                   'HNT/USDT', 'ICX/USDT', 'IOST/USDT', 'IOTA/USDT', 'KAVA/USDT', 'KNC/USDT', 'LINK/USDT', 'LTC/USDT',
                   'MKR/USDT', 'NEO/USDT', 'OMG/USDT', 'ONT/USDT', 'QTUM/USDT', 'REN/USDT', 'RLC/USDT', 'RUNE/USDT', 'SNX/USDT',
                   'SOL/USDT', 'SRM/USDT', 'STORJ/USDT', 'SUSHI/USDT', 'SXP/USDT', 'THETA/USDT', 'TRB/USDT', 'TRX/USDT',
                   'UNI/USDT', 'VET/USDT', 'WAVES/USDT', 'XLM/USDT', 'XMR/USDT', 'XRP/USDT', 'XTZ/USDT', 'YFII/USDT',
                   'YFI/USDT', 'ZEC/USDT', 'ZIL/USDT', 'ZRX/USDT']


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
