# from .constants import *
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from scraper.models import Submission, Comment
from .constants import *
import praw
import pytz
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Scrape reddit posts'

    def add_arguments(self, parser):
        # add arguments to control the type of post scraping (i.e. top, new, hot)
        pass

    def handle(self, *args, **options):

        new_posts = list()
        updated_posts = list()

        reddit = praw.Reddit(
                        client_id     = CLIENT_ID,
                        client_secret = CLIENT_SECRET,
                        user_agent    = USERAGENT)

        for sub in SUBS_TO_SCRAPE:
            subreddit = reddit.subreddit(sub)
            
            for sub in subreddit.top("all", limit=6):
                try:
                    if '[meta]' not in sub.title:
                        d = dict()
                        d['subreddit']    = sub.subreddit.display_name
                        d['title']        = sub.title
                        d['author']       = sub.author.name
                        d['sub_id']       = sub.id
                        d['url']          = sub.url
                        d['score']        = int(sub.score)
                        d['selftext']     = sub.selftext
                        d['text_len']     = len(sub.selftext)
                        d['created_time'] = pytz.utc.localize(datetime.utcfromtimestamp(sub.created_utc))

                        try:
                            sub_exists = Submission.objects.get(sub_id = sub.id)
                            # below needs a test
                            if sub_exists.text_len == len(sub.selftext):
                                pass
                            else:
                                self.stdout.write(self.style.SUCCESS(f'Post changes detected at {sub.id}. Proceed scraping...'))
                                s = Submission
                                s(**d).save()
                                updated_posts.append(d['title'])
                        except:
                            self.stdout.write(self.style.SUCCESS(f'No existing post found for {sub.id}. Proceed scraping...'))
                            s = Submission
                            s(**d).save()
                            new_posts.append(d['title'])

                            # get comments
                            sub.comment_sort = 'hot'
                    
                            for c in sub.comments[:5]:
                                com = Comment
                                submission = s.objects.get(sub_id = sub.id)
                                com(body=c.body, submission=submission).save()
                except:
                    self.stdout.write(self.style.WARNING(f'Error. Skipping.'))
        if len(new_posts) > 0:
            msg = 'The following new posts have been scraped:\n\n'
            for p in new_posts:
                msg = msg + '\t' + p + '\n'

        if len(updated_posts) > 0:
            msg += '\nThe following posts have been updated and scraped again:\n\n'
            for p in updated_posts:
                msg = msg + '\t' + p + '\n'

        if len(msg) > 0:
            send_mail(
                'New or updated posts scraped.',
                msg,
                'elder.dk@gmail.com',
                ['elder.dk@gmail.com'],
                fail_silently=False,
            )