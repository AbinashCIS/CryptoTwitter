'''
Author: Abinash Sinha
Email: abinash.s@cisinlabs.com
Organisation: CIS India

Compute for each tweet a sentiment score with Vader (named compound) and a score linked to the popularity of the tweet and its compound.
'''
import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tqdm import tqdm
from utils import get_filepath


class Analyzer():
    def __init__(self, currency):
        self.clean_file, self.root_filepath = get_filepath(currency=currency)
        self.df_clean = pd.read_csv(self.clean_file)
        print(self.df_clean.head(5))

    def analyze(self):
        self.df_clean = self.df_clean.sort_values(
            by='ID')  # the bigger the ID, the most recent the tweet
        analyzer = SentimentIntensityAnalyzer()
        compound = []
        for i, s in enumerate(tqdm(self.df_clean['Text'])):
            vs = analyzer.polarity_scores(s)
            compound.append(vs["compound"])
        self.df_clean["compound"] = compound

        scores = []
        for i, s in tqdm(self.df_clean.iterrows(),
                         total=self.df_clean.shape[0]):
            scores.append(s["compound"] * ((s["UserFollowerCount"] + 1)) *
                          ((s["Likes"] + 1)))
        self.df_clean["score"] = scores
        print(self.df_clean.head(5))
        filepath = os.path.join(self.root_filepath, 'tweets_with_score.csv')
        f = open(filepath, "a+", encoding='utf-8')
        self.df_clean.to_csv(f,
                             mode='a',
                             encoding='utf-8',
                             index=False,
                             header=False)
        f.close()

    def split_by_date(self, row_size: int = 2000):
        from datetime import datetime
        n = row_size
        chunks_df = [
            self.df_clean[i:i + n] for i in range(0, self.df_clean.shape[0], n)
        ]
        sep_char = '~'
        for chunk_df in chunks_df:
            chunk_min = chunk_df['ID'].min()
            chunk_max = chunk_df['ID'].max()
            date_from = (datetime.strptime(
                chunk_df.iloc[0]['CreatedAt'],
                '%a %b %d %X %z %Y')).strftime('%Y-%m-%d %H-%M-%S')
            date_to = (datetime.strptime(
                chunk_df.iloc[-1]['CreatedAt'],
                '%a %b %d %X %z %Y')).strftime('%Y-%m-%d %H-%M-%S')
            print(date_from, date_to)

            # Write into csv
            chunk_df.to_csv(
                f"{self.root_filepath}/{date_from}{sep_char}{date_to}.csv",
                header=True,
                index=False)
