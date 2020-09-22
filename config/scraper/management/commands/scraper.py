# from .constants import *
from datetime import datetime

import praw
import pytz
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from scraper.models import Comment, Submission
from decouple import config, Csv


class Command(BaseCommand):
    help = 'Scrape reddit posts'

    def add_arguments(self, parser):
        # add arguments to control the type of post scraping (i.e. top, new, hot)
        parser.add_argument(
            '--scope', 
            nargs='?', 
            const='top', 
            default='top', 
            type=str,
            help='Deterine the scope of scraping i.e. top or hot'
            )
        parser.add_argument(
            '--limit', 
            nargs='?', 
            const=5, 
            default=5, 
            type=int,
            help='Maximum number to scrape from each subreddit'
            )

    def handle(self, *args, **options):

        new_posts = list()
        updated_posts = list()

        reddit = praw.Reddit(
                        client_id     = config('CLIENT_ID'),
                        client_secret = config('CLIENT_SECRET'),
                        user_agent    = config('USERAGENT')
                        )

        for subreddit in config('SUBS_TO_SCRAPE', cast=Csv()):
            subred = reddit.subreddit(subreddit)
            if options['scope'] == 'top':
                subred = subred.top("all", limit=options['limit'])
                print(f"scraping top with limit of {options['limit']}")
            else:
                subred = subred.hot(limit=options['limit'])
                print(f"scraping hot with limit of {options['limit']}")
            
            for submission in subred:
                try:
                    if '[meta]' not in submission.title:
                        d = dict()
                        d['subreddit'] = submission.subreddit.display_name
                        d['title'] = submission.title
                        d['author'] = submission.author.name
                        d['sub_id'] = submission.id
                        d['url'] = submission.url
                        d['score'] = int(submission.score)
                        d['selftext'] = submission.selftext
                        d['text_len'] = len(submission.selftext)
                        d['created_time'] = pytz.utc.localize(datetime.utcfromtimestamp(submission.created_utc))

                        try:
                            sub_exists = Submission.objects.get(sub_id = submission.id)
                            # below needs a test
                            if sub_exists.text_len == len(submission.selftext):
                                pass
                            else:
                                self.stdout.write(self.style.SUCCESS(f'Post changes detected at {submission.id}. Proceed scraping...'))
                                s = Submission
                                s(**d).save()
                                updated_posts.append(d['title'])
                        except:
                            self.stdout.write(self.style.SUCCESS(f'No existing post found for {submission.id}. Proceed scraping...'))
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
