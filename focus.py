import re, json, requests
from datetime import datetime, timedelta
import tweepy
from pprint import pprint

from settings import TWITTER_KEYS, threshold, retweet_threshold, censor


def elevate(tweet):
    username = tweet.user.screen_name
    if username in threshold:
       if tweet.favorite_count < threshold[username]:
           return False

    if username in retweet_threshold:
       if tweet.retweet_count < retweet_threshold[username]:
           return False

    if username in censor:
        phrases = censor[username]
        for p in phrases:
            if re.search(p, tweet.full_text) is not None:
                return False

    return True

consumer_key = TWITTER_KEYS['consumer_key']
consumer_secret = TWITTER_KEYS['consumer_secret']
access_token_key = TWITTER_KEYS['access_token_key']
access_token_secret = TWITTER_KEYS['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline(count = 40, tweet_mode = 'extended')

blocked_count = 0
for tweet in public_tweets:
    if elevate(tweet):
        print("{} - {} [{}/{}]: {}".format(tweet.user.screen_name,tweet.created_at,tweet.favorite_count,tweet.retweet_count,tweet.full_text))
    else:
        blocked_count += 1

print(dir(public_tweets[0]))
print("Blocked {} of {} posts.".format(blocked_count, len(public_tweets)))
# api.update_status( msg) 

