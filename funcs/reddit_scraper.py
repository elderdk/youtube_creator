from constants import *
import praw
from colorama import init
from colorama import Fore, Back, Style
init()

reddit = praw.Reddit(
                    client_id=CLIENT_ID, 
                    client_secret=CLIENT_SECRET,
                    user_agent=USERAGENT)

subreddit = reddit.subreddit('relationship_advice')



# import sys
# for sub in subreddit.hot(limit=10):
#     sys.stdout.buffer.write(sub.title.encode('utf-8'))
#     print('\n')

for sub in subreddit.hot(limit=5):
    print(sub.id)
    print(sub.title.encode('utf-8'))
    print()
    sub.comment_sort = 'hot'
    for c in sub.comments[:5]:
        print(Fore.GREEN + c.body + Style.RESET_ALL)
        

# for submission in top_subreddit:
#     topics_dict["title"].append(submission.title)
#     topics_dict["score"].append(submission.score)
#     topics_dict["id"].append(submission.id)
#     topics_dict["url"].append(submission.url)
#     topics_dict["comms_num"].append(submission.num_comments)
#     topics_dict["created"].append(submission.created)
#     topics_dict["body"].append(submission.selftext)