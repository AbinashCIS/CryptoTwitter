'''
Author: Abinash Sinha
Email: abinash.s@cisinlabs.com
Organisation: CIS India

'''
from time import sleep
from twython import Twython
import pandas as pd
from tqdm import tqdm
import re


class TweetExtractor():
    '''
    This aims to retrieve tweets, clean them in order to observe a correlation between crypto currencies and tweets' sentiments. 
    The following steps are executed :

    - Retrieve tweets with Twython API (Twitter API wrapper for python)
    - Extract the wanted data (tweet's text, #followers, #likes, etc.)
    - Clean the textual data (remove unnecessary elements like media, websites link, pseudos, ...)
    '''
    def __init__(self,
                 app_key: str,
                 app_secret: str,
                 currency: str,
                 currency_symbol=None) -> None:
        self.APP_KEY = app_key
        self.APP_SECRET = app_secret
        self.currency = currency
        self.currency_symbol = currency_symbol

        self.twitter = Twython(self.APP_KEY, self.APP_SECRET, oauth_version=2)
        self.ACCESS_TOKEN = self.twitter.obtain_access_token()
        self.twitter = Twython(self.APP_KEY, access_token=self.ACCESS_TOKEN)
        self.rate_limit_status = self.twitter.get_application_rate_limit_status(
        )['resources']['search']

    def __str__(self) -> str:
        limit = self.rate_limit_status["/search/tweets"]["limit"]
        remaining = self.rate_limit_status["/search/tweets"]["remaining"]
        return f'Currency={self.currency} Rate Limit <Remaining={remaining} Limit={limit}>'

    def __repr__(self) -> str:
        limit = self.rate_limit_status["/search/tweets"]["limit"]
        remaining = self.rate_limit_status["/search/tweets"]["remaining"]
        return f'<Currency={self.currency},Remaining={remaining},Limit={limit}>'

    def get_tweets(self, num_queries: int, file: str) -> None:
        '''
        The following fields are retrieved from the response:

        - id (int) : unique identifier of the tweet
        - text (string) : UTF-8 textual content of the tweet, max 140 chars
        - user
        - name (string) : twitter's pseudo of the user
        - followers_count (int) : Number of followers the user has
        - retweet_count (int) : Number of times the tweet has been retweeted
        - favorite_count (int) : Number of likes
        - created_at (datetime) : creation date and time of the tweet

        Also, we wanted to retrieve the following fields but it is not possible with the standard free API, 
        Enterprise or premium is needed (https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object.html)

        - reply_count (int) : Number of times the Tweet has been replied to

        We used the search opertators to not only search by hashtag but also the tweets that contain the currency name 
        or that have the hashtag with the currency's abreviation. 
        (https://lifehacker.com/search-twitter-more-efficiently-with-these-search-opera-1598165519) 
        
        '''
        NUMBER_OF_QUERIES = num_queries
        tweets_raw_file = file
        data = {"statuses": []}
        next_id = ""
        query = f'#{self.currency} OR #{self.currency_symbol}'
        with open(tweets_raw_file, "a+", encoding='utf-8') as f:
            if not next_id:
                f.write(
                    "ID,Text,UserName,UserFollowerCount,RetweetCount,Likes,CreatedAt\n"
                )
                f.flush()
            last_size = 0
            for i in tqdm(range(NUMBER_OF_QUERIES)):
                if not next_id:
                    data = self.twitter.search(
                        q=query, lang='en', result_type='recent',
                        count="100")  # Use since_id for tweets after id
                else:
                    data["statuses"].extend(
                        self.twitter.search(q=query,
                                            lang='en',
                                            result_type='mixed',
                                            count="100",
                                            max_id=next_id)["statuses"])
                if len(data["statuses"]) > 1:
                    next_id = data["statuses"][len(data["statuses"]) - 1]['id']
                if last_size + 1 == len(data["statuses"]):
                    break
                else:
                    last_size = len(data["statuses"])
            print(f'Retrieved {len(data["statuses"])},')
            d = pd.DataFrame([[
                s["id"], s["text"].replace('\n', '').replace(
                    '\r', ''), s["user"]["name"], s["user"]["followers_count"],
                s["retweet_count"], s["favorite_count"], s["created_at"]
            ] for s in data["statuses"]],
                             columns=('ID', 'Text', 'UserName',
                                      "UserFollowerCount", 'RetweetCount',
                                      'Likes', "CreatedAt"))
            d.to_csv(f, mode='a', encoding='utf-8', index=False, header=False)
            if last_size + 1 == len(data["statuses"]):
                print('No more new tweets, stopping...')
            data["statuses"] = []

    def clean_data(self, raw_file: str, clean_file: str) -> None:
        '''
        Now we will cleanup the data.

        We already filtered tweets in english in the call to the Twitter API.
        We will now filter links, @Pseudo, images, videos, unhashtag #happy -> happy.

        We won't transform to lower case because Vader take capital letters into consideration to emphasize sentiments.
        '''
        tweets_raw_file = raw_file
        tweets_clean_file = clean_file

        d = pd.read_csv(tweets_raw_file)
        for i, s in enumerate(tqdm(d['Text'])):
            text = d.loc[i, 'Text']
            text = text.replace("#", "")
            text = re.sub('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',
                          '',
                          text,
                          flags=re.MULTILINE)
            text = re.sub('@\\w+ *', '', text, flags=re.MULTILINE)
            d.loc[i, 'Text'] = text
        f = open(tweets_clean_file, 'a+', encoding='utf-8')
        d.to_csv(f, header=True, encoding='utf-8', index=False)
