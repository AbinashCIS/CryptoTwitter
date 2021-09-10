'''
Author: Abinash Sinha
Email: abinash.s@cisinlabs.com
Organisation: CIS India

Command line tool for twitter crypto sentiment analysis
'''

import os
import argparse
from processor.extractor import TweetExtractor
from analysis.sentiment import Analyzer
from settings import logger


def parse_args():
    logger.info("sdfsfd")
    parser = argparse.ArgumentParser(
        description='Command line tool for twitter crypto sentiment analysis',
        usage='crypto [options]',
        add_help=True,
        epilog='Enjoy!!')
    parser.add_argument('-c',
                        '--currency',
                        help='currency to analyze',
                        default='BTC')
    parser.add_argument('-e',
                        '--extract',
                        action='store_true',
                        default=False,
                        help='extract data from twitter API')
    parser.add_argument('-n',
                        '--number-of-tweets',
                        default=20,
                        type=int,
                        help='set the number of tweets to be fetched')
    parser.add_argument('-a',
                        '--analyze',
                        action='store_true',
                        help='Run analysis on the data')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help='print more output data')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.extract:
        from settings import APP_KEY, APP_SECRET
        currency = args.currency
        extractor = TweetExtractor(app_key=APP_KEY,
                                   app_secret=APP_SECRET,
                                   currency=currency)
        raw_file_path = extractor.get_tweets(num_queries=20)
        clean_file_path = extractor.clean_data()
        print(raw_file_path, clean_file_path)
    if args.analyze:
        currency = args.currency
        analyzer = Analyzer(currency=currency)
        analyzer.analyze()
        analyzer.split_by_date()
