import sys
from os import path
import os
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
import requests
import json
import tweepy
from credentials import getCredentials
import re
from pprint import pprint
from google.cloud import language_v1
from google.cloud.language_v1 import enums
import time
# get path to script's directory
currdir = path.dirname(__file__)

def create_wordcloud(trend_topic,text):
    mask = np.array(Image.open(path.join(currdir, "cloud.png")))
    stopwords = set(STOPWORDS)
    stopwords.update(["que", "quê", "da", "meu", "em", "você",
                      "de", "ao", "os", "tá", "se", "né", "dá"])
    wc = WordCloud(background_color="white",
                                    max_words=200,
                                    mask=mask,
                   stopwords=stopwords)
    wc.generate(text)
    wc.to_file(path.join('img/', str(trend_topic+".png")))
            
def get_trend_topics():
    api = getCredentials('twitter')
    BRAZIL_WOE_ID = 23424768
    brazil_trends = api.trends_place(BRAZIL_WOE_ID)
    trends = json.loads(json.dumps(brazil_trends, indent=1))
    # pprint (trends)
    trend_topics = trends[0]["trends"]
    for t in trends[0]["trends"]:
        print (t["name"]) 
    # for trend in trends[0]["trends"]:
    create_data(trend_topics,api)
    
def create_data(trend_topics,api):
    for idx, trend in enumerate(trend_topics):
        print (trend["name"])
        # trend_topic = (trend["name"]).strip("#")
        trend_topic = (trend["name"])
        query = trend["query"]
        text = search_tweets(query,api)
        create_wordcloud(trend_topic,text)
        sentiment = analyze_sentiment(text)
        if (idx+1) % 10 == 0:
            break
                
def search_tweets(query,api):
    text = ''
    for tweet_info in tweepy.Cursor(api.search, q=query, tweet_mode='extended').items(400):
        if 'retweeted_status' in dir(tweet_info):
            tweet=tweet_info.retweeted_status.full_text
        else:
            tweet=tweet_info.full_text
            tweet = re.sub(r'http\S+', '', tweet)
            # print(text)
            tweet = re.sub('\W+', ' ', tweet)
            # print(tweet)
            text += str(tweet) + " "
    print(text)
    return text

def analyze_sentiment(text_content):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"
    client = language_v1.LanguageServiceClient()
    # text_content = 'I am so happy and joyful.'
    print("aaa")
    # Available types: PLAIN_TEXT, HTML
    type_ = enums.Document.Type.PLAIN_TEXT
    # language = "en"
    document = {"content": text_content, "type": type_}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = enums.EncodingType.UTF8
    response = client.analyze_sentiment(document, encoding_type=encoding_type)
    # Get overall sentiment of the input document
   
    sentiment = response.document_sentiment.score
    print (sentiment)
    return sentiment
        
if __name__ == "__main__":
    get_trend_topics()

