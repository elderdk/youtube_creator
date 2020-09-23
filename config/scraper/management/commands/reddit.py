import praw
from decouple import config


def reddit():
    reddit = praw.Reddit(
        client_id     = config('CLIENT_ID'),
        client_secret = config('CLIENT_SECRET'),
        user_agent    = config('USERAGENT')
        )
    return reddit