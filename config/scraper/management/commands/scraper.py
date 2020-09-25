from datetime import datetime

import pytz
from decouple import Csv, config
from django.core.management.base import BaseCommand

from scraper.models import Comment, Submission

from .reddit import reddit
from .send_email import make_email_body, send_email


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

        new_posts = []
        updated_posts = []

        for submission in subred:

            parsed_dict = self.make_dict(submission)

            if not parsed_dict:
                continue

            else:
                submisssison, created = Submission.objects\
                                .update_or_create(
                                    sub_id=parsed_dict['sub_id'],
                                    defaults=parsed_dict
                                    )

                if created:
                    new_posts.append(submission.title)

                    # get comments
                    submission.comment_sort = COMMENT_SORT

                    for c in submission.comments[:MAX_COMMENTS]:
                        parent_sub = Submission.objects.get(
                            sub_id=submission.id
                            )
                        Comment(body=c.body, submission=parent_sub).save()

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

        if new or updated:
            email_body = make_email_body(new, updated)
            send_email(email_body)
