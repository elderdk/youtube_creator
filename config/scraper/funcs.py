# from .constants import *
from datetime import datetime
from .models import Submission, Comment
import praw

def make_subs():
    CLIENT_ID      = 'gNnuhR4Z226Dbg'
    CLIENT_SECRET  = 'OGGJLRMgheENVfuGWbpYXa9JT1U'
    USERAGENT      = 'dke_scraper for /u/No-Nectarine-4394'
    SUBS_TO_SCRAPE = [
        'offmychest',
        'relationship_advice',
        'AmItheAsshole',
        'confession',
        'tifu',
        ]

    reddit = praw.Reddit(
                    client_id     = CLIENT_ID,
                    client_secret = CLIENT_SECRET,
                    user_agent    = USERAGENT)

    submissions = list()
    for sub in SUBS_TO_SCRAPE:
        subreddit = reddit.subreddit(sub)
        
        for sub in subreddit.hot(limit=3):
            if not sub.title.startswith('[meta]'):
                d = dict()
                d['subreddit']    = sub.subreddit.display_name
                d['title']        = sub.title
                d['author']       = sub.author.name
                d['sub_id']       = sub.id
                d['url']          = sub.url
                d['score']        = int(sub.score)
                d['selftext']     = sub.selftext
                d['text_len']     = len(sub.selftext)
                d['created_time'] = datetime.utcfromtimestamp(sub.created_utc)

                print(sub.title.encode('utf-8'))
                
                submissions.append(d)
                
                sub = Submission
                sub(**d).save()

                # get comments
                # comm = list()
                # sub.comment_sort = 'hot'
                # for c in sub.comments[:5]:
                #     comm.append(c.body)
                # d['comments'] = comm

    return submissions