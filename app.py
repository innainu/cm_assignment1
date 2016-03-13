'''''
OAUTH stuff ADAPTED FROM:
http://whichlight.com/blog/twitter-oauth-in-python-with-tweepy-and-flask/

scrollable table code adapted from:
http://www.bootply.com/JnOYtO9xzn

'''''

import flask 
import tweepy
import datetime
from flask import Flask, render_template, redirect
from flask import request, url_for
from datetime import date
app = Flask(__name__)
app.debug = True
from analysis import get_topics, get_similar

#config

CONSUMER_TOKEN="riTWHAuyhvr7BfE4gcehUg83V"
CONSUMER_SECRET="5Z03juskBxPIuAoD560WOg6GZXzfWNsTAjPsEnHgQ49Aworw16"
CALLBACK_URL = 'http://localhost:5000/verify'
session = dict()
db = dict() 
topics = dict()
topic_dict = dict()

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



@app.route("/discoverhashtags", methods=['GET'])
def hashtag_discovery():
    print "hd", topics

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
                topic_dict[topic][kw] = get_similar.return_query(api,kw, week_before, today)

            # topic_dict['topic'+ str(topics.index(topic))].append(get_similar.return_query(api,kw, week_before, today))
    
    print "type", type(topic_dict)
    print "topic_dict2", topic_dict
    return flask.render_template('hashtag_discovery.html', topic_dict = topic_dict)


if __name__ == "__main__":
    app.run()