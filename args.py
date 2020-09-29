import argparse
import sys

def parse():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Core'
        )
    )

    # parser.add_argument('--backtest', default=False, required=True,
    #                     help='Backtest or live trade?')

    parser.add_argument('--exchange', default='', required=False,
                        help='Exchange')

    parser.add_argument('--ticker', default='', required=False,
                        help='Ticker')
    
    parser.add_argument('--base', default='', required=False,
                        help='Base Currency')
    parser.add_argument('--quote', default='', required=False,
                        help='Quote Currency')
    
    parser.add_argument('--data_timeframe', default='', required=False,
                        help='Timeframe of provided data')

    parser.add_argument('--resample_timeframe', default='weekly', required=False,
                        choices=['daily', 'weekly', 'monhtly'],
                        help='Timeframe to resample to')
    
    # parser.add_argument('--production', default=False, required=True,
    #                     help='Run in production?')
    
    parser.add_argument('--compression', default=1, required=False, type=int,
                        help='Compress n bars into 1')
    
    parser.add_argument('--plot', default=False, required=False, type=bool,
                        help='To plot or not to plot')

    # Backtest from & to datetime
    parser.add_argument('--from_date', required='--backtest' in sys.argv,
                        type=int, help='From date')
    parser.add_argument('--from_month', required='--backtest' in sys.argv,
                        type=int, help='From month')
    parser.add_argument('--from_year', required='--backtest' in sys.argv,
                        type=int, help='From year')
    parser.add_argument('--to_date', required='--backtest' in sys.argv,
                        type=int, help='To Date')
    parser.add_argument('--to_month', required='--backtest' in sys.argv,
                        type=int, help='To month')
    parser.add_argument('--to_year', required='--backtest' in sys.argv,
                        type=int, help='To year')

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--strategy', required=True, default='',
                        metavar='kwargs')
    parser.add_argument('--exectype', required=True, default='',
                        metavar='kwargs')

    return parser.parse_args()
