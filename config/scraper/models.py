from django.db import models
from datetime import datetime
# from .constants import * # causes ImportError: attempted relative import with no known parent package
import praw

# Create your models here.
class Submission(models.Model):
    subreddit    = models.CharField(max_length = 50)
    title        = models.CharField(max_length = 500)
    author       = models.CharField(max_length = 30)
    sub_id       = models.CharField(max_length = 7)
    url          = models.CharField(max_length = 200)
    score        = models.IntegerField()
    selftext     = models.TextField()
    text_len     = models.IntegerField()
    created_time = models.DateTimeField()
    scraped_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    body       = models.TextField()


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
                
                submissions.append(d)
                
                sub = Submission()
                sub(**d).save()

                # get comments
                comm = list()
                sub.comment_sort = 'hot'
                for c in sub.comments[:5]:
                    comm.append(c.body)
                d['comments'] = comm

    return submissions