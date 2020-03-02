from __future__ import print_function

import twitter
from t import consumer_key, consumer_secret, access_secret, access_token
import json


def get_tweets(api=None, screen_name=None):
    timeline = api.GetUserTimeline(screen_name=screen_name, count=200)
    earliest_tweet = min(timeline, key=lambda x: x.id).id
    print("getting tweets before:", earliest_tweet)

    while True:
        tweets = api.GetUserTimeline(
            screen_name=screen_name, max_id=earliest_tweet, count=200
        )
        new_earliest = min(tweets, key=lambda x: x.id).id

        if not tweets or new_earliest == earliest_tweet:
            break
        else:
            earliest_tweet = new_earliest
            print("getting tweets before:", earliest_tweet)
            timeline += tweets

    return timeline


api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token,
                  access_token_secret=access_secret)

screen_name = 'realDonaldTrump'
print("Getting tweets from", screen_name)
timeline = get_tweets(api=api, screen_name=screen_name)

with open('timeline.json', 'w+') as f:
    for tweet in timeline:
        print(tweet.text)
        f.write(json.dumps(tweet._json))
        f.write('\n')
