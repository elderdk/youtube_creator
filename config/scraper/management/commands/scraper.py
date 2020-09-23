# from .constants import *
from datetime import datetime

import pytz
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from scraper.models import Comment, Submission
from decouple import config, Csv
from .reddit import reddit


MAX_COMMENTS = 5
COMMENT_SORT = 'hot'

class Command(BaseCommand):
    help = 'Scrape reddit posts'

    def add_arguments(self, parser):
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

    def make_email_body(self, new_posts, updated_posts):
        if len(new_posts) > 0:
            msg = '\n'.join(new_posts)
            title = 'The following new posts have been scraped:\n\n'
            msg.append(title, 0)

        if len(updated_posts) > 0:
            msg.append('\n\nThe following posts have been updated and scraped again:\n\n')
            msg.append('\n'.join(updated_posts))

        return msg

    def send_email(self, email_body):
            
        send_mail(
            'New or updated posts scraped.',
            email_body,
            config('SENDER_EMAIL'),
            [config('RECEIVER_EMAIL')],
            fail_silently=False,
            )

    def handle(self, *args, **options):

        new_posts = list()
        updated_posts = list()

        red = reddit()

        for subreddit in config('SUBS_TO_SCRAPE', cast=Csv()):
            subred = red.subreddit(subreddit)

            if options['scope'] == 'top':
                subred = subred.top("all", limit=options['limit'])
            else:
                subred = subred.hot(limit=options['limit'])
            
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
                                sub = Submission
                                sub(**d).save()
                                updated_posts.append(d['title'])
                        except:
                            self.stdout.write(self.style.SUCCESS(f'No existing post found for {submission.id}. Proceed scraping...'))
                            sub = Submission
                            sub(**d).save()
                            new_posts.append(d['title'])

                            # get comments
                            submission.comment_sort = COMMENT_SORT
                    
                            for c in submission.comments[:MAX_COMMENTS]:
                                com = Comment
                                parent_sub = sub.objects.get(sub_id = submission.id)
                                com(body=c.body, submission=parent_sub).save()
  
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error. Skipping. {e}'))
            
        email_body = make_email_body(new_posts, updated_posts)

        if any(new_posts, updated_posts):
            send_email(email_body)
