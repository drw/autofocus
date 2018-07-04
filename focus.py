import sys, re, json, requests
from datetime import datetime, timedelta
import tweepy
import fire
from pprint import pprint

from settings import TWITTER_KEYS, threshold, retweet_threshold, censor

def connect_to_twitter():
    consumer_key = TWITTER_KEYS['consumer_key']
    consumer_secret = TWITTER_KEYS['consumer_secret']
    access_token_key = TWITTER_KEYS['access_token_key']
    access_token_secret = TWITTER_KEYS['access_token_secret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)
    api = tweepy.API(auth)
    return api

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

def list(username=None):
    api = connect_to_twitter()
    if username == None:
        me = api.me()
        username = me.screen_name

    following_ids = api.friends_ids(id=username)
    following = [api.get_user(id=i).screen_name for i in following_ids]
    pprint(following)

def follow(username):
    api = connect_to_twitter()
    user = api.create_friendship(id=username,follow=True) # This method returns a user object

def unfollow(username):
    api = connect_to_twitter()
    user = api.destroy_friendship(id=username) # This method returns a user object

def posts(*args,**kwargs):
    target_user = kwargs.get('target_user',None)
    api = connect_to_twitter()

    if target_user is None:
        tweets = api.home_timeline(count = 100, tweet_mode = 'extended') # public tweets
    else:
        tweets = api.user_timeline(id = target_user, count = 100, tweet_mode = 'extended')

    blocked_count = 0
    for tweet in tweets:
        if elevate(tweet):
            print("{} - {} [{}/{}]: {}".format(tweet.user.screen_name,tweet.created_at,tweet.favorite_count,tweet.retweet_count,tweet.full_text))
        else:
            blocked_count += 1

    print("Blocked {} of {} posts.".format(blocked_count, len(tweets)))
    # api.update_status( msg) 

    # tweet.entities.hashtags should be a list of tags

# sys.argv[1] specifies user to focus on
# > python3 focus.py <username> # pulls the last N posts for @username (even if not 
# following that user), allowing rapid iteration and design of the filter parameters
# for that user.

if __name__ == '__main__':
    if len(sys.argv) == 1:
        posts()
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['list','following']:
            list()
        else:
            target_user = sys.argv[1]
            posts(target_user = target_user)
    else:
        fire.Fire()
