import tweepy
from nltk import WordPunctTokenizer, re
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from t import consumer_key, consumer_secret, access_secret, access_token
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="creds.json"


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
    document = types\
               .Document(content=tweet,
                         type=enums.Document.Type.PLAIN_TEXT)
    sentiment_score = client\
                      .analyze_sentiment(document=document)\
                      .document_sentiment\
                      .score
    return sentiment_score


def main():
    tweets = get_tweets('realDonaldTrump')
    for tweet in tweets:
        if not tweet.full_text.startswith("RT @"):
            print(get_sentiment_score(tweet.full_text))


if __name__ == '__main__':
    main()