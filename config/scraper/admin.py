import re
from datetime import datetime
from pathlib import Path
import shutil

from django.contrib import admin
from django.utils.text import slugify
from django.contrib import messages
from django.utils.translation import ngettext
from django.http import FileResponse

from .models import Comment, Submission


TMP_FOLDER = Path("./scraper/tmp")
FNAME = "{dt}_{subreddit}_{sub_id}_{slug_title}.txt"

# Register your models here.
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    passdate_hierarchy = 'scraped_time'
    list_display = ('sub_id', 'subreddit', 'score', 'title', 'scraped_time')

    actions = ['download']

    def divide_per_line(self, msg):

            sentences = re.findall('\s+[^.!?]*[.!?]', msg)
            return '\n'.join([s.strip() for s in sentences])

    def download(self, request, submissions):

        for sub in submissions:
            slug_title = slugify(sub.title, allow_unicode=True)
            dt = datetime.strftime(sub.created_time, '%Y%m%d')
            fname = TMP_FOLDER.joinpath(
                        FNAME.format(
                            dt=dt,
                            subreddit=sub.subreddit,
                            sub_id=sub.sub_id,
                            slug_title=slug_title[:30],
                        ))
            with fname.open(mode='w') as f:
                text = """
                {title}
                /r/{subreddit}

                Author: {author}
                URL: {url}

                {text_body}                              
                """.format(
                    title = sub.title,
                    subreddit = sub.subreddit,
                    author = sub.author,
                    url = sub.url,
                    text_body = self.divide_per_line(sub.selftext)
                )

                f.write(text)     

        self.message_user(request, ngettext(
            '%d file downloaded',
            '%d files downloaded',
            submissions,
            ) % len(submissions), messages.SUCCESS)

        # Below is for creating a zip file and auto-initiating download.
        # Below should be moved to another file later for aesthetics.
        
        # Currently the zip file is saved in the root folder (i.e. /config)
        # This should be fixed so that download.zip is saved and cleaned up after downloading.

        zf_file = shutil.make_archive(
            TMP_FOLDER.joinpath('download').name, 
            'zip', 
            TMP_FOLDER
            )

        response = FileResponse(
            open(zf_file, 'rb'), 
            as_attachment=True
            )

        response['Content-Disposition'] = f"attachment; filename={zf_file.split('/')[-1]}"

        # Clean the TMP_FOLDER
        for f in TMP_FOLDER.glob('*.txt'):
            f.unlink()

        return response
        
    download.short_description = "Download the selected files"

admin.site.register(Comment)
