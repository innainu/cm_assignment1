'''''
OAUTH stuff ADAPTED FROM:
http://whichlight.com/blog/twitter-oauth-in-python-with-tweepy-and-flask/

scrollable table code adapted from:
http://www.bootply.com/JnOYtO9xzn

'''''

import flask 
import tweepy
import datetime
import local_config
from flask import Flask, render_template, redirect
from flask import request, url_for
from datetime import date
app = Flask(__name__)
app.debug = True
from analysis import get_topics, get_similar

#config
CONSUMER_TOKEN = local_config.CONSUMER_TOKEN
CONSUMER_SECRET = local_config.CONSUMER_SECRET
CALLBACK_URL = local_config.CALLBACK_URL
IMDB_API_KEY = local_config.IMDB_API_KEY


session = dict()
db = dict() 
topics = dict()
topic_dict = dict()
movies = []

@app.route("/")
def send_token():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, 
        CONSUMER_SECRET, 
        CALLBACK_URL)
    try: 
        #get the request tokens
        redirect_url= auth.get_authorization_url()
        session['request_token']= (auth.request_token)
    except tweepy.TweepError:
        print 'Error! Failed to get request token'
    #this is twitter's url for authentication
    return flask.redirect(redirect_url) 

@app.route("/verify", methods=['GET'])
def get_verification():
    #get the verifier key from the request url
    verifier = request.args['oauth_verifier']
    print "verifier", verifier
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    token = session['request_token']
    del session['request_token']
    # auth.set_access_token(str(token[0]), str(token[1]))
    auth.request_token = token
    # try:
    auth.get_access_token(verifier)
    # except tweepy.TweepError:
        # print 'Error! Failed to get access token.'

    #now you have access!
    api = tweepy.API(auth)

    #store in a "db"
    db['api']=api
    db['access_token_key']=auth.access_token
    db['access_token_secret']=auth.access_token_secret
    return flask.redirect(flask.url_for('start'))

@app.route("/start",methods=['GET', 'POST'])
def start():
    #auth done, app logic can begin
    api = db['api']

    #get 100 statuses to use for model
    if len(topics) == 0:
        user_timeline = api.user_timeline(count = 100)
        statuses = []
        for status in user_timeline:
            statuses.append(status._json)

        #create a topic model and display your topics
        corpus, dictionary = get_topics.construct_corpus(statuses)
        top_topics = get_topics.lda_model(corpus, dictionary)
        print "top_topics1", top_topics
        print "len(top_topics)", len(top_topics)

        for r in top_topics:
            topics[top_topics.index(r)] = []
            for t in r[0]:
                topics[top_topics.index(r)].append(t[1])
    
    if request.method == 'POST':
        return redirect(url_for('hashtag_discovery'))

    return flask.render_template('tweets.html', topics=topics)



@app.route("/discoverhashtags", methods=['GET', 'POST'])
def hashtag_discovery():
    # print "hd", topics

    if not topic_dict:
        api = db['api']

        #search over the past week
        today  = str(date.today())
        week_before = str(date.today()- datetime.timedelta(days=7))

        #get topics
        # topic_dict = {}
        
        for topic in topics:
            topic_dict[topic] = {}
            for kw in topics[topic]:
                topic_dict[topic][kw], hashtags = get_similar.return_query(api,kw, week_before, today)

        for r in hashtags:
            movies.append(get_similar.get_movies(r, IMDB_API_KEY))
        
    if request.method == 'POST':
        return redirect(url_for('get_movies'))
        
    # print "type", type(topic_dict)
    # print "topic_dict2", topic_dict
    return flask.render_template('hashtag_discovery.html', topic_dict = topic_dict)

@app.route("/getmovies", methods=['GET', 'POST'])
def get_movies():
    return flask.render_template('movies.html', movies = movies)

if __name__ == "__main__":
    app.run()