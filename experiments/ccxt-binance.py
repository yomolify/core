import ccxt
binance = ccxt.binance({
    "apiKey": "RmjJYeuCEhMbIUjg8Cq3x0ZgXXlWOmxoWlATfB9SF3ypZpJvCdr5nNKQwwgmpe0b",
    "secret": "YstqwOxKpekt6whhTPYlDiF0IdyQbbZpH6RzDKqvCsveHi66vXmYLJl4Jb7ZBild",
    "verbose": False,
})
print(binance.create_market_buy_order('BTC/USDT', 0.001))

