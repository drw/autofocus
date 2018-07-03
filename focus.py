import sys, re, json, requests
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

def main(*args,**kwargs):

    target_user = kwargs.get('target_user',None)
    consumer_key = TWITTER_KEYS['consumer_key']
    consumer_secret = TWITTER_KEYS['consumer_secret']
    access_token_key = TWITTER_KEYS['access_token_key']
    access_token_secret = TWITTER_KEYS['access_token_secret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    api = tweepy.API(auth)

    if target_user is None:
        tweets = api.home_timeline(count = 40, tweet_mode = 'extended') # public tweets
    else:
        tweets = api.user_timeline(id = target_user, count = 40, tweet_mode = 'extended')

    blocked_count = 0
    for tweet in tweets:
        if elevate(tweet):
            print("{} - {} [{}/{}]: {}".format(tweet.user.screen_name,tweet.created_at,tweet.favorite_count,tweet.retweet_count,tweet.full_text))
            #if tweet.user.screen_name == 'a_baronca':
            #    for k in dir(tweet):
            #        if k[0] != '_' and k not in ['retweets']:
            #            print(k)
            #            pprint(getattr(tweet,k))
        else:
            blocked_count += 1

    print(dir(tweets[0]))
    print("Blocked {} of {} posts.".format(blocked_count, len(tweets)))
    # api.update_status( msg) 

    # tweet.entities.hashtags should be a list of tags

# sys.argv[1] specifies user to focus on
if __name__ == '__main__':
    if len(sys.argv) > 1:
        target_user = sys.argv[1]
        main(target_user = target_user)
    else:
        main()
