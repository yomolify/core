import pandas as pd
import pandas_datareader.data as web
import backtrader as bt
import numpy as np
from datetime import datetime 

data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
table = data[0]
tickers = table[1:][0].tolist()
pd.Series(tickers).to_csv("spy/tickers.csv")