from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse
import pandas as pd
import numpy as np
import datetime
from scipy.stats import norm
import math
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import glob
import ntpath


def parse_args():
    parser = argparse.ArgumentParser(description='MultiData Strategy')

    parser.add_argument('--Custom_Alg',
                        default=False, # True OR False... NOT 'True' OR 'False'
                        help='True = Use custom alg')

    parser.add_argument('--SLTP_On',
                        default=True, # True OR False... NOT 'True' OR 'False'
                        help='True = Use Stop-Loss & Take-Profit Orders, False = do NOT use SL & TP orders')

    parser.add_argument('--stoploss',
                        action='store',
                        default=0.10, type=float,
                        help=('sell a long position if loss exceeds'))

    parser.add_argument('--takeprofit',
                        action='store',
                        default=2.00, type=float,
                        help=('Exit a long position if profit exceeds'))

    parser.add_argument('--data0', '-d0',
                        default=r'T:\PD_Stock_Data\DBLOAD',
                        help='Directory of CSV data source')


    parser.add_argument('--fromdate', '-f',
                        default='2012-01-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', '-t',
                        default='2013-12-31',
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--limitpct',
                        action='store',
                        default=0.005, type=float,
                        help=('For buying at LIMIT, this will only purchase if the price is less than (1-limitpct)*Closing price'))

    parser.add_argument('--validdays',
                        action='store',
                        default=30, type=int,
                        help=('The number of days which a buy order remains valid'))

    parser.add_argument('--sellscore',
                        action='store',
                        default=-0.91, type=float,
                        help=('Max score for a sell'))

    parser.add_argument('--marketindex',
                        default='XJO',
                        help='XAO = All Ords, XJO = ASX200')

    parser.add_argument('--startingcash',
                        default=100000, type=int,
                        help='Starting Cash')

    parser.add_argument('--minholddays',
                        default=3, type=int,
                        help='Dont exit a market position until have held stock for at least this many days (excl. Stop-Loss and TP). May assist stopping exiting/cancelling orders when they are still being accepted by broker (i.e. day after entering mkt).')

    parser.add_argument('--pctperstock',
                        action='store', #0.083 = 1/12... i.e. a portfolio of up to 12 stocks
                        default=0.083, type=float, #i.e. 10% portfolio value in each stock
                        help=('Pct of portfolio starting cash to invest in each stock purchase'))

    parser.add_argument('--maxpctperstock',
                        action='store',
                        default=0.20, type=float,
                        help=('Max pct portfolio to invest in any porticular stock'))

    parser.add_argument('--mintrade',
                        default=1000, type=float,
                        help='Smallest dollar value to invest in a stock (if cash level below amount required for pctperstock)')

    parser.add_argument('--tradefee',
                        default=10.0, type=float,
                        help='CMC Markets Fee per stock trade (BUY OR SELL)')

    parser.add_argument('--alg_buyscore', #only used if Custom_Alg ==True
                        action='store',  # 0.91884558
                        default=0.91, type=float,
                        help=('Min score for a buy'))

    return parser.parse_args()

#Excel sheet with ASX200 index constituents (used for chosing stocks to analyse in Backtrader)
def LoadIndicies(Excel_Path, Excel_Sheet):
    # Load ASX200 Excel File
    ASX200 = pd.read_excel(Excel_Path, sheetname=Excel_Sheet)
    Index_Constituents = ASX200.to_dict(orient='list')
    for key, value in Index_Constituents.items():
        Index_Constituents[key] = [x for x in value if str(x) != 'nan']  # drop any "blank" (NaN) tickers from the index constituents table
    IndexDates = sorted(Index_Constituents.keys())
    IndexDates.append(datetime.datetime.now().strftime("%Y-%m-%d"))  # ordered list of the Index constituent Dates, with todays date at the end
    return Index_Constituents, IndexDates

def LoadStockData(CSV_path=None):
    args = parse_args()
    if CSV_path is None:
        raise RuntimeError("no stock folder directory specifed.")
    allFiles = glob.glob(CSV_path + "/*.csv")
    Stocks = {}  # Create a DICTIONARY object to store the entire contents of all dataframes, allows for easy reference to / looping through dataframes by a string of their name, i.e. : 'CSL'
    for file_ in allFiles:
        name = ntpath.basename(file_[:-4])  # Set DF name = basename (not path) of the CSV.  [:-4] gets rid of the '.CSV' extention.
        Stocks[name] = pd.read_csv(file_, index_col='Date', parse_dates=True, header=0)
    return Stocks


class StockLoader(btfeeds.PandasData):
    args = parse_args()
    params = (
        ('openinterest', None),     # None= column not present
        ('TOTAL_SCORE', -1))        # -1 = autodetect position or case-wise equal name
    if args.Custom_Alg == True:
        lines = ('TOTAL_SCORE',)
    if args.Custom_Alg == True:
        datafields = btfeeds.PandasData.datafields + (['TOTAL_SCORE'])
    else:
        datafields = btfeeds.PandasData.datafields

class st(bt.Strategy):
    args = parse_args()
    params = ( #NB: self.p = self.params
        ('printlog', True),
    )

    def log(self, txt, dt=None, doprint=False):
        if self.p.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s - %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order = {} #Order: market entry
        self.order_out = {} #Order: market exit
        self.order_sl = {} #Stop-Loss
        self.order_tp = {} #Take-Profit
        self.bar_executed = {}
        self.sma_short = {}
        self.sma_long = {}
        for i, d in enumerate(d for d in self.datas):
            self.order[d._name] = None
            self.order_out[d._name] = None
            self.order_sl[d._name] = None
            self.order_tp[d._name] = None
            self.bar_executed[d._name] = None

            self.sma_short[d._name] = bt.indicators.SimpleMovingAverage(d, period=42) #np.round(pd.rolling_mean(d.Close, window=42),2)
            self.sma_long[d._name] = bt.indicators.SimpleMovingAverage(d, period=252) #np.round(pd.rolling_mean(d.Close, window=252),2)


    def start(self):
        pass

    def notify_trade(self, trade): #NB: "print(Trade.__dict__)"
        if trade.isclosed: #Market Position exited
            self.log('OPERATION PROFIT: %s, Gross: %2f, Net: %2f' %(trade.data._name,
                                                                    trade.pnl,
                                                                    trade.pnlcomm))

    def notify_order(self, order):

        #used to check order info
        ord = self.order[order.data._name]
        ord_out = self.order_out[order.data._name]
        ord_sl = self.order_sl[order.data._name]
        ord_tp = self.order_tp[order.data._name]

        if order.status in [order.Submitted, order.Accepted]:
            return #do nothing

        elif order.status in [order.Margin, order.Rejected, order.Completed, order.Cancelled]:
            if order.isbuy():
                buysell = 'BUY'
            elif order.issell():
                buysell = 'SELL'

            if ord and order == ord:
                type = 'Enter'
                self.bar_executed[order.data._name] = len(order.data) #length of dataframe when enter market (used to calc days held)
            elif ord_out and order == ord_out:
                type = 'Exit'
            elif ord_sl and order == ord_sl:
                type = 'Stop-Loss'
            elif ord_tp and order == ord_tp:
                type = 'Take-Profit'

            self.log('%s %s: %s, Type: %s, Ref: %s, Price: %.2f, Cost: %.2f, Size: %.2f, Comm %.2f' %(buysell,
                                                                                                      order.Status[order.status],
                                                                                                      order.data._name,
                                                                                                      type,
                                                                                                      order.ref,
                                                                                                      order.executed.price,
                                                                                                      order.executed.value,
                                                                                                      order.executed.size,
                                                                                                      order.executed.comm))

        if not order.alive():# indicate no order is pending, allows new orders
            if ord and order == ord:
                self.order[order.data._name] = None

            elif ord_out and order == ord_out:
                self.order_out[order.data._name] = None

            elif ord_sl and order == ord_sl:
                self.order_sl[order.data._name] = None

            elif ord_tp and order == ord_tp:
                self.order_tp[order.data._name] = None

    def prenext(self): #overrides PRENEXT() so that the "NEXT()" calculations runs regardless of when each stock data date range starts.
        self.next()

    def next(self):
        today = self.getdatabyname(args.marketindex).datetime.date(0)
        weekday = today.isoweekday() #Monday = 1, Sunday = 7
        if weekday in range(1,8): # analyse on all weekdays (MONDAY to SUNDAY)
            num_long = 0 #number long stocks
            #IdealLongPortf = pd.DataFrame(columns=('Stock', 'Score','Close','Current Position', 'Ideal Position', 'Pos Delta Value', 'Go NoGo')) #ideal stock positions at end of each next() iteration
            for i, d in enumerate(d for d in self.datas if len(d) and d._name != args.marketindex):  # Loop through Universe of Stocks. "If Len(d)" is used to check that all datafeeds have delivered values. as if using minute data, some may have had many minutes, 500, and another may not have 1 record yet (if its still on daily)
                position = self.broker.getposition(d)
                positiondol = float(self.broker.getposition(d).size*d.close[0])
                cash = self.broker.getcash() #total available cash

                if position.size == 0 \
                        and self.order[d._name] is None \
                        and self.order_out[d._name] is None \
                        and self.order_sl[d._name] is None \
                        and self.order_tp[d._name] is None \
                        and d.close[0] > 0 \
                        and self.sma_short[d._name][0] > self.sma_long[d._name][0]:
                        #and d.lines.TOTAL_SCORE[0] >= args.alg_buyscore:

                    #IdealLongPortf.append([d._name, d.lines.TOTAL_SCORE[0], d.close[0], position.size, np.NaN, np.NaN,np.NaN])
                    buylimit = d.close[0]*(1-args.limitpct)

                    if args.SLTP_On == True:
                        stop_loss = d.close[0]*(1.0 - args.stoploss)
                        take_profit = d.close[0]*(1.0 + args.takeprofit)

                        o1 = self.buy(data = d,
                                      exectype=bt.Order.Limit,
                                      price=buylimit,
                                      valid=today + datetime.timedelta(days=args.validdays),
                                      transmit=False)
                        self.log('CREATE BUY: %s, Close: %2f, Buy @: %2f, Oref: %i, Score: %2f' %(d._name,
                                                                                                  d.close[0],
                                                                                                  buylimit,
                                                                                                  o1.ref,
                                                                                                  1)) #d.lines.TOTAL_SCORE[0]))

                        o2 = self.sell(data = d,
                                       size = o1.size,         # could be an issue with re-balancing!!!
                                       exectype=bt.Order.Stop,
                                       price=stop_loss,
                                       parent=o1,
                                       transmit=False)
                        self.log('CREATE Stop-Loss: %s, Sell Stop @: %2f, Oref: %i' %(d._name, stop_loss, o2.ref))

                        o3 = self.sell(data = d,
                                       size = o1.size,
                                       exectype=bt.Order.Limit,
                                       price=take_profit,
                                       parent=o1,
                                       transmit=True)
                        self.log('CREATE Take-Profit: %s, Sell Limit @: %2f, Oref: %i' %(d._name, take_profit, o3.ref))

                        self.order[d._name] = o1
                        self.order_sl[d._name] = o2
                        self.order_tp[d._name] = o3
                    else:
                        o1 = self.buy(data = d,
                                      exectype=bt.Order.Limit,
                                      price=buylimit,
                                      valid=today + datetime.timedelta(days=args.validdays))
                        self.log('CREATE BUY: %s, Close: %2f, Buy @: %2f, Oref: %i, Score: %2f' %(d._name,
                                                                                                  d.close[0],
                                                                                                  buylimit,
                                                                                                  o1.ref,
                                                                                                  1)) #d.lines.TOTAL_SCORE[0]))
                        self.order[d._name] = o1

                elif position.size > 0: # Currently LONG
                    daysheld = len(d) - self.bar_executed[d._name] + 1
                    self.log('Stock Held: %s, Close: %2f, Posn: %i, Posn($): %2f, Hold Days: %i, Score: %2f, Score Yest: %2f' %(d._name,
                                                                                                                               d.close[0],
                                                                                                                               position.size,
                                                                                                                               positiondol,
                                                                                                                               daysheld,
                                                                                                                               1, #d.lines.TOTAL_SCORE[0],
                                                                                                                               1)) #d.lines.TOTAL_SCORE[-1]))

                    num_long +=1

                    if self.order[d._name] is None \
                        and self.order_out[d._name] is None \
                        and daysheld >= args.minholddays \
                        and self.sma_short[d._name][0] < self.sma_long[d._name][0]:
                        #and d.lines.TOTAL_SCORE[0] < args.alg_buyscore:
                        self.log('CLOSING LONG POSITION: %s, Close: %2f, Score: %2f' %(d._name,
                                                                                 d.close[0],
                                                                                 1)) #d.lines.TOTAL_SCORE[0]))

                        # cancel SL/TP 1st to avoid possibility of duplicate exit orders
                        if self.order_sl[d._name]:
                            self.log('CANCELLING SL & TP for: %s, SL ref: %i, TP ref: %i' %(d._name,self.order_sl[d._name].ref, self.order_tp[d._name].ref))
                            self.broker.cancel(self.order_sl[d._name]) #this automatically cancels the TP too
                        #if self.order_tp[d._name]:
                        #    self.log('CANCELLING TP for: %s, ref: %s' %(d._name,self.order_tp[d._name].ref))
                        #    self.broker.cancel(self.order_tp[d._name])

                        o4 = self.close(data=d)
                        self.order_out[d._name] = o4

            totalwealth = self.broker.getvalue()
            cash = self.broker.getcash()
            invested = totalwealth - cash

            self.log("Stocks Held: %s, Total Wealth: %i, Invested: %i, Cash-On-Hand: %i" %(str(num_long),
                                                                                           totalwealth,
                                                                                           invested,
                                                                                           cash))

    def stop(self):
        pass

class PortfolioSizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        args = parse_args()
        position = self.broker.getposition(data)
        price = data.close[0]
        investment = args.startingcash * args.pctperstock
        if cash < investment:
            investment = max(cash,args.mintrade) # i.e. never invest less than the "mintrade" $value
        qty = math.floor(investment/price)

        # This method returns the desired size for the buy/sell operation
        if isbuy:  # if buying
            if position.size < 0:  # if currently short, buy the amount which are short to close out trade.
                 return -position.size
            elif position.size > 0:
                return 0  # dont buy if already hold
            else:
                return qty  # num. stocks to LONG

        if not isbuy:  # if selling..
            if position.size < 0:
                return 0  # dont sell if already SHORT
            elif position.size > 0:
                return position.size  # currently Long... sell what hold
            else:
                return qty  # num. stocks to SHORT


def RunStrategy():
    args = parse_args()
    cerebro = bt.Cerebro()
    cerebro.addstrategy(st)
    # strats = cerebro.optstrategy(st,maperiod=range(10, 31))

    #date range to backtest
    tradingdates = Stocks[args.marketindex].loc[
        (Stocks[args.marketindex].index>=datetime.datetime.strptime(args.fromdate, "%Y-%m-%d")) &
        (Stocks[args.marketindex].index<datetime.datetime.strptime(args.todate, "%Y-%m-%d"))
    ]

    #Load 200 stocks into Backtrader (specified in the Index_constituents list)
    for ticker in Index_Constituents[IndexDates[3]]:
        datarange = Stocks[ticker].loc[
            (Stocks[ticker].index>=datetime.datetime.strptime(args.fromdate, "%Y-%m-%d")) &
            (Stocks[ticker].index<datetime.datetime.strptime(args.todate, "%Y-%m-%d"))
        ]
        #REINDEX to make sure the stock has the exact same trading days as the MARKET INDEX. Reindex ffill doesn't fill GAPS. Therefore also apply FILLNA
        datarange.reindex(tradingdates.index, method='ffill').fillna(method='ffill',inplace=True)
        data = StockLoader(dataname=datarange)
        data.plotinfo.plot=False
        cerebro.adddata(data, name=ticker)

    data = btfeeds.PandasData(dataname=tradingdates, openinterest=None) #load market index (for date referencing)
    cerebro.adddata(data, name=args.marketindex)

    #cerebro.addanalyzer(CurrentBuysAnalyzer, )
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, ) #length of holds etc
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Years, riskfreerate=0.03, annualize=True)
    cerebro.addanalyzer(bt.analyzers.SQN)
    cerebro.addanalyzer(bt.analyzers.DrawDown, )

    cerebro.broker.setcash(args.startingcash) # set starting cash
    cerebro.addsizer(PortfolioSizer)

    commission = float(args.tradefee/(args.pctperstock*args.startingcash))
    print("The Commission rate is: %0.5f" % (commission))
    cerebro.broker.setcommission(commission=commission)

    cerebro.run(runonce=False, writer=True)
    cerebro.plot(volume=False, stdstats=False)
    '''
    zdown=True: Rotation of the date labes on the x axis
    stdstats=False: Disable the standard plotted observers
    numfigs=1: Plot on one chart
    '''

if __name__ == '__main__':
    # if python is running this script (module) as the main program, then __name__ == __main__, and this block of code will run.
    #  However, if another script (module) is IMPORTING this script (module), this block of code WILL NOT RUN, but the above functions can be called.
    args = parse_args()
    t1 = datetime.datetime.now()
    print('Processing Commenced: {}'.format(str(t1)))

    #Load stocks from local drive for analysis
    Stocks = LoadStockData(args.data0)
    t2 = datetime.datetime.now()

    # Dictionary of Index Constituents (and their stock dataframes)
    Index_Constituents, IndexDates = LoadIndicies(
        Excel_Path='T:\Google Drive\Capriole\CAPRIOLEPROCESSOR\TickerUpdater.xlsm',
        Excel_Sheet='ASX200_Const_Updated')
    print('ASX200 constituent list date: {}'.format(IndexDates[3]))

    if args.Custom_Alg == True:
        initiate()
        t3 = datetime.datetime.now()

    RunStrategy()
    t4 = datetime.datetime.now()

    #TIMER
    print('Run-time - TOTAL: {0}'.format(datetime.datetime.now() - t1))
    print('Run-time - Load Data: {0}'.format(t2 - t1))
    if t3:
        print('Run-time - Algorithm: {0}'.format(t3 - t2))
        print('Run-time - Strategy Back-test: {0}'.format(t4 - t3))
    else:
        print('Run-time - Strategy Back-test: {0}'.format(t4 - t2))