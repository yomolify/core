import json
import backtrader as bt

def addAnalyzers(cerebro):
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Years, factor=365)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name='sharpe_ratio_a')
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', factor=365)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name='transactions')
    # cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

    # cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')


def getAnalysis(stat):
    # printTradeAnalysis(stat.trade_analyzer.get_analysis())
    printSQN(stat.sqn.get_analysis())
    printSummary(stat)

def printTradeAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    #Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    win_percent = round((total_won / total_closed) * 100, 2)
    #Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Win Percentage','Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed,total_won,total_lost]
    r2 = [win_percent, win_streak, lose_streak, pnl_net]
    #Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    #Print the rows
    print_list = [h1,r1,h2,r2]
    row_format ="{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))

def printSQN(analyzer):
    sqn = round(analyzer.sqn,2)
    print('SQN: {}'.format(sqn))

def printSummary(stat):
    print('Sharpe Ratio: ', json.dumps(stat.sharpe_ratio.get_analysis()["sharperatio"], indent=2))
    # print('Sharpe Ratio: ', round(json.dumps(stat.sharpe_ratio.get_analysis()["sharperatio"], indent=2), 2))
    print('Sharpe Ratio Annualized: ', json.dumps(stat.sharpe_ratio_a.get_analysis()["sharperatio"], indent=2))
    print('Max Drawdown: ', json.dumps(stat.drawdown.get_analysis().max.drawdown, indent=2))
    print('Max Moneydown: ', json.dumps(stat.drawdown.get_analysis().max.moneydown, indent=2))
    print('Max Drawdown Length: ', json.dumps(stat.drawdown.get_analysis().max.len, indent=2))
    print('Annual Return:', json.dumps(stat.annual_return.get_analysis(), indent=2))
    # print('VWR: ', json.dumps(stat.vwr.get_analysis()["vwr"], indent=2))
    # print('Number of Trades: ', json.dumps(stat.trade_analyzer.get_analysis().total.total, indent=2))

    # print(json.dumps(stat.returns.get_analysis(), indent=2))

    # print('Sharpe Ratio:', stat.sharpe_ratio.get_analysis())
    # print('Returns:', stat.returns.get_analysis())
    # print('Maximum Drawdown:', stat.drawdown.get_analysis())
    # print('Trade Analyzer:', stat.trade_analyzer.get_analysis())
    # print('Transactions:', stat.transactions.get_analysis())
    # print('Variability-Weighted Return:', stat.vwr.get_analysis())
    # print('SQN:', stat.sqn.get_analysis())
