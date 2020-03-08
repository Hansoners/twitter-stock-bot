import json

import quandl
import tweepy
from nltk import WordPunctTokenizer, re
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from t import consumer_key, consumer_secret, access_secret, access_token, quandl_key
from googlesearch import search
import time
import yfinance as yf
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"
quandl.ApiConfig.api_key = quandl_key


def authentication(consumer_key, consumer_secret, account_token, account_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(account_token, account_secret)
    api = tweepy.API(auth)
    return api


def get_tweets(screen_name):
    api = authentication(consumer_key, consumer_secret, access_token, access_secret)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200, tweet_mode="extended")
    tweets = new_tweets
    return tweets


def clean_tweet(tweet):
    link_removed = re.sub('https?://[A-Za-z0-9./]+', '', tweet)
    number_removed = re.sub('[^a-zA-Z]', ' ', link_removed)
    lower_case_tweet = number_removed.lower()
    tok = WordPunctTokenizer()
    words = tok.tokenize(lower_case_tweet)
    clean_tweet = (' '.join(words)).strip()
    return clean_tweet


def get_sentiment_score(tweet):
    client = language.LanguageServiceClient()
    document = types \
        .Document(content=tweet,
                  type=enums.Document.Type.PLAIN_TEXT)
    sentiment_score = client \
        .analyze_sentiment(document=document) \
        .document_sentiment \
        .score
    return sentiment_score


def get_ticker(name):
    val = 'yahoo finance ' + name
    link = []
    for url in search(val, tld='es', lang='es', stop=1):
        link.append(url)

    link = str(link[0])
    link = link.split("/")
    if link[-1] == '':
        ticker = link[-2]
    else:
        x = link[-1].split('=')
        ticker = x[-1]

    return ticker


def get_price(stock_ticker, price_type, price_date):
    try:
        if price_type == 'close':
            return yf.Ticker(stock_ticker).history(start=price_date, end=price_date).Close[0]
        elif price_type == 'open':
            return yf.Ticker(stock_ticker).history(start=price_date, end=price_date).Open[0]
    except:
        return 0


def date_convert(price_date):
    return time.strftime('%Y-%m-%d', time.strptime(price_date, '%a %b %d %H:%M:%S +0000 %Y'))


def get_position(tweet_sentiment):
    if tweet_sentiment > 0.3:
        position = 'Long Position'
    elif tweet_sentiment < -0.3:
        position = 'Short Position'
    else:
        position = 'Do Nothing'
    return position


def get_profit(position, open_price, close_price, cur_profit):
    if position == 'Long Position':
        cur_profit += (close_price - open_price)
    elif position == 'Short Position':
        cur_profit += (open_price - close_price)
    return cur_profit


def contains_word(s, w):
    return (' ' + w + ' ') in (' ' + s + ' ')


def main():
    # Get dictionary - company:ticker
    f = open('company_dict.json')
    company_dict = json.load(f)
    f.close()

    profit = 0


    ## Scrape New Donald Trump Tweets
    # tweets = get_tweets('realDonaldTrump')
    # for tweet in tweets:
    #     if not tweet.full_text.startswith("RT @"):
    #         for company in dow_list:
    #             if company.lower() in clean_tweet(tweet.full_text):
    #                 print("text '%s' contains phrase '%s'" % (tweet.full_text, company))

    # Using Old Tweets
    with open('trump_archive.json') as data_file:
        print('Loading tweets from @realDonaldTrump')
        tweets = json.load(data_file)
        for tweet in tweets:
            if not tweet['is_retweet']:
                for company in company_dict.keys():
                    if contains_word(clean_tweet(tweet['text']), company.lower()):
                        tweet_sentiment = get_sentiment_score(tweet['text'])
                        ticker = company_dict[company]
                        price_date = date_convert(tweet['created_at'])
                        close_price = get_price(ticker, 'close', price_date)
                        open_price = get_price(ticker, 'open', price_date)
                        difference = close_price - open_price
                        position = get_position(tweet_sentiment)
                        profit = get_profit(position, open_price, close_price, profit)

                        if close_price != 0:
                            print("Tweet: '%s'\n"
                                  "Date: %s\n"
                                  "Company Mentioned: %s\n"
                                  "Sentiment: %s\n"
                                  "Position: %s\n"
                                  "Open: %s\n"
                                  "Close: %s\n"
                                  "Difference: %s\n"
                                  "Total Profit/Loss: %s\n"
                                  % (tweet['text'],
                                     price_date,
                                     company,
                                     tweet_sentiment,
                                     position,
                                     open_price,
                                     close_price,
                                     difference,
                                     profit
                                     ))


if __name__ == '__main__':
    main()
