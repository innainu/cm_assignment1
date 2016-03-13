#since we are doing 3 topics with 3 top words each, that is 9 queries.
#we need 5000 data points total, so I'm just going to do 400 items each query

import tweepy

def return_query(api,topic, week_before, today):
    statuses = []
    for status in tweepy.Cursor(api.search, q = topic ,since=week_before, until=today).items(20):
        #only append if tweet has a status
        if status._json['entities']['hashtags']:
            statuses.append([status._json['user']['screen_name'],status._json['user']['followers_count'],status._json['text'],status._json['entities']['hashtags']])
    #sort statuses by number of followers of the user 
    sorted(statuses, key=lambda x: x[1], reverse = True)
    return statuses