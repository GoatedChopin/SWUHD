import tweepy
import pandas as pd
import numpy as np

apikey = 'api key'
apisecretkey = 'secret key'

access_token = 'access token'
access_token_secret = 'secret access token'

auth = tweepy.OAuthHandler(apikey,apisecretkey)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)

last_day = pd.to_datetime('2021/3/29')
first_day = pd.to_datetime('2020/3/6')

public_tweets = [tweet for tweet in tweepy.Cursor(api.user_timeline,id='swuhealth').items() if tweet.created_at > first_day]
np.savez('public_tweets',public_tweets)
tweets_file = np.load('public_tweets.npz',allow_pickle=True)
tweets_array = tweets_file['arr_0']
print(tweets_array)