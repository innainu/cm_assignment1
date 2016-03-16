#since we are doing 2 topics with 2 top words each, that is 9 queries.
#we need 5000 data points total, so I'm just going to do 400 items each query

import tweepy
import tmdbsimple as tmdb
tmdb.API_KEY = '9ee5856b7bd983ecdcd57c5ad226e1f6'

def get_movies(top_topics):
    all_movie_matches = []
    for tag in top_topics:
        search = tmdb.Search()
        response = search.movie(query=tag)
        for result in search.results:
            all_movie_matches.append(result['title'])
    return all_movie_matches

def return_query(api,topic, week_before, today):
    statuses = []
    for status in tweepy.Cursor(api.search, q = topic ,since=week_before, until=today).items(400):
        #only append if tweet has a status
        if status._json['entities']['hashtags']:
            statuses.append([status._json['user']['screen_name'],status._json['user']['followers_count'],status._json['text'],status._json['entities']['hashtags']])
    hashtags = set()
    for status in statuses:
        for ht in status[3]:
            hashtags.add(ht['text'])
    #sort statuses by number of followers of the user 
    sorted(statuses, key=lambda x: x[1], reverse = True)
    return statuses, list(hashtags)
