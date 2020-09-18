import praw

reddit = praw.Reddit(client_id="CLIENT_ID", client_secret="CLIENT_SECRET",
                     password="PASSWORD", user_agent="USERAGENT",
                     username="USERNAME")