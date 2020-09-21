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


# Register your models here.
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    passdate_hierarchy = 'scraped_time'
    list_display = ('sub_id', 'subreddit', 'score', 'title', 'scraped_time')

    actions = ['download']

    def download(self, request, submissions):

        def _divide_per_line(msg):
            sentences = re.findall('\s+[^.!?]*[.!?]', msg)
            return '\n'.join([s.strip() for s in sentences])

        for sub in submissions:
            slug_title = slugify(sub.title, allow_unicode=True)
            dt = datetime.strftime(sub.created_time, '%Y%m%d')
            tmp_folder = Path("./scraper/tmp")
            fname = tmp_folder.joinpath(f"{dt}_{sub.subreddit}_{sub.sub_id}_{slug_title[:20]}.txt")
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

        # Below is for creating a zip file and auto-initiating download.
        # Below should be moved to another file later for aesthetics.
        
        # Currently the zip file is saved in the root folder (i.e. /config)
        # This should be fixed so that download.zip is saved and cleaned up after downloading.
        zf_file = shutil.make_archive(tmp_folder.joinpath('download').name, 'zip', tmp_folder)
        response = FileResponse(open(zf_file, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f"attachment; filename={zf_file.split('/')[-1]}"

        # Clean the tmp_folder
        for f in tmp_folder.glob('*.txt'):
            f.unlink()

        return response
        
    download.short_description = "Download the selected files"

admin.site.register(Comment)
