import os
import pandas as pd


def view_tweets(file: str, num_lines: int) -> None:
    '''
    Open a given csv file, read content, print to stdout.

    Args 
        - file : path to file
        - num_line - number of lines to view
    Return 
        - None
    '''
    df_clean = pd.read_csv(file)
    print(df_clean.head(num_lines))


def get_filepath(currency: str) -> tuple:
    path = os.path.join('data', currency)
    if os.path.exists(path):
        filenames = next(os.walk(path), (None, None, []))[2]
        if 'clean_tweets.csv' in filenames:
            return (os.path.join(path, 'clean_tweets.csv'), path)
    else:
        return None
