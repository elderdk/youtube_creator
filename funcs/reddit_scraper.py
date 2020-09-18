from constants import *
import praw

reddit = praw.Reddit(
                    client_id=CLIENT_ID, 
                    client_secret=CLIENT_SECRET,
                    user_agent=USERAGENT)

subreddit = reddit.subreddit('relationship_advice')

import sys


for sub in subreddit.hot(limit=10):
    sys.stdout.buffer.write(sub.title.encode('utf-8'))
    print('\n')

# for submission in top_subreddit:
#     topics_dict["title"].append(submission.title)
#     topics_dict["score"].append(submission.score)
#     topics_dict["id"].append(submission.id)
#     topics_dict["url"].append(submission.url)
#     topics_dict["comms_num"].append(submission.num_comments)
#     topics_dict["created"].append(submission.created)
#     topics_dict["body"].append(submission.selftext)