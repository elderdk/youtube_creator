# from .constants import *
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from scraper.models import Submission, Comment
from django.utils.text import slugify
import re


class Command(BaseCommand):
    help = 'Scrape reddit posts'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def divide_per_line(self, msg):
        sentences = re.findall('\s+[^.!?]*[.!?]', msg)
        return '\n'.join([s.strip() for s in sentences])

    def handle(self, *args, **options):

        undelivered_subs = Submission.objects.filter(downloaded = False)
        file_list = list()

        for sub in undelivered_subs:
            slug_title = slugify(sub.title, allow_unicode=True)
            dt = datetime.strftime(sub.created_time, '%Y%m%d')
            with open(f"{dt}_{sub.subreddit}_{sub.sub_id}_{slug_title[:20]}.txt", 'w') as f:
                text = """
                {title}
                /r/{subreddit}

                Author: {author}
                URL: {url}

                {text_body}                              
                """.format(
                    title     = sub.title.strip(),
                    subreddit = sub.subreddit.strip(),
                    author    = sub.author.strip(),
                    url       = sub.url.strip(),
                    text_body = self.divide_per_line(sub.selftext)
                )

                f.write(text)                
                self.stdout.write(self.style.SUCCESS(f'File created: {slug_title}'))
                