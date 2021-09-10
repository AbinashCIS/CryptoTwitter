'''
Author: Abinash Sinha
Email: abinash.s@cisinlabs.com
Organisation: CIS India

Command line tool for twitter crypto sentiment analysis
'''

import os
import argparse


def parse_args() -> vars:
    parser = argparse.ArgumentParser(
        description='Command line tool for twitter crypto sentiment analysis',
        usage='crypto [options]',
        add_help=True,
        epilog='Enjoy!!')
    parser.add_argument('-c',
                        '--currency',
                        help='currency to analyze',
                        required=True)
    parser.add_argument('-a',
                        '--api',
                        action='store_true',
                        help='Run the REST API')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help='print more output data')

    return vars(parser.parse_args())


if __name__ == '__main__':
    args = parse_args()
    print(args)