import re
from datetime import datetime
from pathlib import Path

from django.contrib import admin
from django.utils.text import slugify
from django.contrib import messages
from django.utils.translation import ngettext

from .models import Comment, Submission


# Register your models here.
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    passdate_hierarchy = 'scraped_time'
    list_display = ('sub_id', 'scraped_time', 'title')

    actions = ['download']

    def download(self, request, submissions):

        def _divide_per_line(msg):
            sentences = re.findall('\s+[^.!?]*[.!?]', msg)
            return '\n'.join([s.strip() for s in sentences])

        file_list = list()

        for sub in submissions:
            slug_title = slugify(sub.title, allow_unicode=True)
            dt = datetime.strftime(sub.created_time, '%Y%m%d')
            fname = Path("./scraper/tmp").joinpath(f"{dt}_{sub.subreddit}_{sub.sub_id}_{slug_title[:20]}.txt")
            with fname.open(mode='w') as f:
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
                    text_body = _divide_per_line(sub.selftext)
                )

                f.write(text)                

                self.message_user(request, ngettext(
                    '%d file downloaded',
                    '%d files downloaded',
                    submissions,
                    ) % len(submissions), messages.SUCCESS)
                    # updated,
                    # ) % updated, messages.SUCCESS)

    download.short_description = "Download the selected files"

admin.site.register(Comment)
