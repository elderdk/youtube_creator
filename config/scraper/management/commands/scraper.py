# from .constants import *
from datetime import datetime

import pytz
from django.db.models import Q
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from scraper.models import Comment, Submission
from decouple import config, Csv
from .reddit import reddit


MAX_COMMENTS = 5
COMMENT_SORT = 'hot'
PROCEED = 'No existing post found for {}. Proceed scraping...'
SKIPPING = 'Existing post found for {}. Skpping...'

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
            new_title = 'The following new posts have been scraped:\n'
            new_posts.insert(0, new_title)

        if len(updated_posts) > 0:
            update_title = '\n\nThe following posts have been updated and scraped again:\n'
            updated_posts.insert(0, update_title)

        return '\n'.join(new_posts) + '\n'.join(updated_posts)

    def send_email(self, email_body):
            
        send_mail(
            'New or updated posts scraped.',
            email_body,
            config('SENDER_EMAIL'),
            [config('RECEIVER_EMAIL')],
            fail_silently=False,
            )

    def make_dict(self, submission):
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
            d['created_time'] = pytz.utc.localize(
                datetime.utcfromtimestamp(submission.created_utc)
                )
            return d

    def update_or_create(self, subred):

        new_posts = list()
        updated_posts = list()

        for submission in subred:
    
            d = self.make_dict(submission)

            if d:
                submisssison, created = Submission.objects\
                                .update_or_create(
                                    sub_id=d['sub_id'],
                                    defaults = d
                                    )

                if created:
                    new_posts.append(submission.title)
                    self.stdout.write(
                        self.style.SUCCESS(
                            PROCEED.format(submission.id)
                            ))

                    # get comments
                    submission.comment_sort = COMMENT_SORT
            
                    for c in submission.comments[:MAX_COMMENTS]:
                        com = Comment
                        parent_sub = Submission.objects.get(
                            sub_id = submission.id
                            )
                        com(body=c.body, submission=parent_sub).save()

            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        SKIPPING.format(submission.id)
                        ))

        return new_posts, updated_posts

    def get_scope(self, subred, options):
        if options['scope'] == 'top':
                subred = subred.top("all", limit=options['limit'])
        else:
            subred = subred.hot(limit=options['limit'])

        return subred

    def handle(self, *args, **options):

        red = reddit()

        for subreddit in config('SUBS_TO_SCRAPE', cast=Csv()):

            subred = red.subreddit(subreddit)
            subred = self.get_scope(subred, options)
            new, updated = self.update_or_create(subred)

        if any([new, updated]):
            email_body = self.make_email_body(new, updated)
            self.send_email(email_body)
