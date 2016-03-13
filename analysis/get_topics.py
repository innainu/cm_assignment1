import sys, unicodedata, gensim 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim import corpora, models, similarities


def remove_punctuation(text):
    #removes punctuation
    # 'S' for special characters
    # 'P' for punctuation
    # 'N' for numbers
    tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
                        if unicodedata.category(unichr(i)).startswith(('S', 'P', 'N')))
    return text.translate(tbl)


def pre_process(test):
    stop = stopwords.words('english')
    #for tweets, append "rt" bc this is at the beginning of every retweet
    stop.append("rt")
    test = test.lower()
    test = remove_punctuation(test)
    test = word_tokenize(test) 
    test = [i for i in test if i not in stop]
    return test

def construct_corpus(tweets):
    words = []
    for r in tweets:
        words.append(pre_process(r['text']))
    dictionary = corpora.Dictionary(words)
    #this convers everything to vectors based on dictionary
    corpus = [dictionary.doc2bow(t) for t in words]
    return corpus, dictionary

def lda_model(corpus, dictionary):
    #splits to 3 topics, but would be better to make this dependent on the number of tweets the user has
    model = gensim.models.LdaModel(corpus, id2word = dictionary, alpha='auto', num_topics=2)
    #get the top 2 relevant words for each topic
    top_topics = model.top_topics(corpus, num_words = 2)
    print len(top_topics)
    return top_topics
    

