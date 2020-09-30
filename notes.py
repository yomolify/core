# CLI

# !!!!!!!! LIVE TRADING !!!!!!!!
nodemon --exec python main.py --exchange=binance --data_timeframe=1m --strategy=BollingerBands.LS1 --exectype=Market --base=BTC --quote=USDT
nodemon --exec python main.py --exchange=binance --ticker=BTCUSDT --data_timeframe=1m --strategy=Misc.BuyHold.BuyAndHold_Buy --exectype=Market

# Debugging to compare values with backtest runs
nodemon --exec python main.py --exchange=binance --ticker=BTCUSDT --data_timeframe=1m --backtest=True --strategy=Misc.BuyHold.BuyAndHold_Buy --exectype=Market --from_year=2017 --from_month=4 --from_date=25 --to_year=2018 --to_month=8 --to_date=26
nodemon --exec python main.py --exchange=binance --ticker=BTCUSDT --data_timeframe=1m --backtest=True --strategy=BollingerBands.L1 --exectype=Market --from_year=2017 --from_month=4 --from_date=25 --to_year=2018 --to_month=8 --to_date=26
nodemon --exec python main.py --exchange=binance --ticker=BTCUSDT --data_timeframe=1m --backtest=True --strategy=Misc.SMA --exectype=Market --from_year=2017 --from_month=4 --from_date=25 --to_year=2018 --to_month=8 --to_date=26

# BNB Backtesting LS1
nodemon main.py --exchange=binance --ticker=BNBUSDT --data_timeframe=1m --backtest=True --strategy=BollingerBands.LS1 --exectype=Market --from_year=2017 --from_month=4 --from_date=25 --to_year=2020 --to_month=8 --to_date=26

# Bitfinex
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2017 --from_month=4 --from_date=25 --to_year=2018 --to_month=8 --to_date=26

# Bitmex
nodemon main.py --exchange=bitmex --ticker=XBTUSD --data_timeframe=1m --from_year=2017 --from_month=4 --from_date=25 --to_year=2018 --to_month=8 --to_date=26

# Binance
nodemon main.py --exchange=binance --ticker=BTCUSDT --data_timeframe=1m --from_year=2017 --from_month=9 --from_date=25 --to_year=2018 --to_month=8 --to_date=26

# April 1st 2015 to May 1st 2015
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2015 --to_month=5 --to_date=1

# -------------- Zurich Long Short ---------------
# In sample for L1 - L7
# April 1st 2015 to April 1st 2018
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=Misc.BuyHold.BuyAndHold_Buy
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L1 
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L2
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L3
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L4
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L5
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L6
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L7
# LS1
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.LS1 --plot=True
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LS3
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.LS3 --plot=True
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=1 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.LS3 --plot=True

nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2017 --from_month=1 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.LS3 --plot=True

# 60% DRAWDOWN PERIOD
# Buy&Hold
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=4 --from_date=1 --to_year=2019 --to_month=4 --to_date=1 --exectype=Market --strategy=Misc.BuyHold.BuyAndHold_Buy --plot=True
# L1
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=2 --from_date=18 --to_year=2019 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L1 
# LS3
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=2 --from_date=18 --to_year=2019 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.LS3 --plot=True
# Small period LS3
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=6 --from_date=1 --to_year=2019 --to_month=2 --to_date=1 --exectype=Market --strategy=BollingerBands.LS3 --plot=True

nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BollingerBands.L7
# All historical data
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2013 --from_month=6 --from_date=1 --to_year=2019 --to_month=3 --to_date=1 --exectype=Market --strategy=BollingerBands.L7

# For bt-ccxt-store to run
nodemon --exec python main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2015 --from_month=4 --from_date=1 --to_year=2018 --to_month=4 --to_date=1 --exectype=Market --strategy=BuyHold.BuyAndHold_Buy

# Out sample for L1 - L7
# June 1st 2013 to April 1st 2015
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2013 --from_month=6 --from_date=1 --to_year=2015 --to_month=4 --to_date=1 --strategy=BuyHold.BuyAndHold_Buy

# April 1st 2018 to March 1st 2019
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=4 --from_date=1 --to_year=2019 --to_month=3 --to_date=1 --strategy=BuyHold.BuyAndHold_Buy

nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=4 --from_date=1 --to_year=2019 --to_month=3 --to_date=1 --exectype=Market --strategy=BollingerBands.L7
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=4 --from_date=1 --to_year=2019 --to_month=3 --to_date=1 --strategy=BuyHold.BuyAndHold_Target
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=4 --from_date=1 --to_year=2019 --to_month=3 --to_date=1 --strategy=BuyHold.BuyAndHold_More
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2018 --from_month=4 --from_date=1 --to_year=2019 --to_month=3 --to_date=1 --strategy=BuyHold.BuyAndHold_More_Fund

# ALL HISTORICAL DATA
# June 1st 2013 to March 1st 2019
nodemon main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2013 --from_month=6 --from_date=1 --to_year=2019 --to_month=3 --to_date=1 --strategy=BollingerBands.L1

# OPTIMIZED (Disables plotting)
nodemon main.py --cerebro exactbars=True,stdstats=False --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2013 --from_month=6 --from_date=1 --to_year=2019 --to_month=3 --to_date=1

# PYPY
nodemon -x pypy3 main.py --exchange=bitfinex --ticker=BTCUSD --data_timeframe=1m --from_year=2013 --from_month=6 --from_date=1 --to_year=2019 --to_month=3 --to_date=1

# Comments
# datapath = os.path.join(modpath, 'data/bitstampUSD_1-min_data_2015-04-01_to_2018-04-01.csv')
# datapath = os.path.join(modpath, 'data/BTC_USD Bitfinex 1d.csv')
# datapath = os.path.join(modpath, 'data/BTCUSDT-1h.csv')
# datapath = os.path.join(modpath, '../Bitfinex-historical-data/BTCUSD/Candles_1m/2013/merged.csv')
# datapath = os.path.join(modpath, '../Bitfinex-historical-data/BTCUSD/Candles_1m/2013/merged.csv')


# BITSTAMP{
# fromdate=datetime.datetime(2016, 4, 1),
# todate=datetime.datetime(2018, 4, 1),}


# BITMEX
# fromdate=datetime.datetime(2013, 4, 25),
# todate=datetime.datetime(2020, 8, 26),


# BINANCE
# fromdate=datetime.datetime(2017, 8, 17),
# todate=datetime.datetime(2020, 8, 1),