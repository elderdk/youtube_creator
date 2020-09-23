import re
import shutil
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from django.contrib import admin, messages
from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse
from django.utils.text import slugify
from django.utils.translation import ngettext

from .models import Comment, Submission

TMP_FOLDER = Path("/tmp")
FNAME = "{dt}_{subreddit}_{sub_id}_{slug_title}"
TXT_BODY = """
{title}
/r/{subreddit}

Author: {author}
URL: {url}

{text_body}                              
"""

# Register your models here.
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    passdate_hierarchy = 'scraped_time'
    list_display = ('sub_id', 'subreddit', 'score', 'title', 'scraped_time')

    actions = ['download']

    def divide_per_line(self, msg):

            sentences = re.findall('\s+[^.!?]*[.!?]', msg)
            return '\n'.join([s.strip() for s in sentences])

    def make_zip(self, tmp_files):
        with NamedTemporaryFile(prefix='download', suffix='.zip') as zf_file:
            with ZipFile(zf_file, 'w') as myzip:
                for txt_file in tmp_files:
                    myzip.write(txt_file.name)
                    txt_file.close()

            response = FileResponse(
                open(zf_file.name, 'rb'), 
                as_attachment=True
                )

            response['Content-Disposition'] = f"attachment; filename={zf_file.name}"
        
        return response

    def make_tmp_files(self, submissions):
        tmp_files = list()

        for sub in submissions:
            slug_title = slugify(sub.title, allow_unicode=True)
            dt = datetime.strftime(sub.created_time, '%Y%m%d')

            fname = FNAME.format(
                            dt=dt,
                            subreddit=sub.subreddit,
                            sub_id=sub.sub_id,
                            slug_title=slug_title[:30],    
            )

            tfile = NamedTemporaryFile(suffix='.txt', prefix=fname)

            text = TXT_BODY.format(
                        title = sub.title,
                        subreddit = sub.subreddit,
                        author = sub.author,
                        url = sub.url,
                        text_body = self.divide_per_line(sub.selftext)
                    )

            tfile.write(bytes(text, 'utf-8'))
            tfile.flush()
            tmp_files.append(tfile)

        return tmp_files

    def download(self, request, submissions):

        tmp_files = self.make_tmp_files(submissions)

        zip_response = self.make_zip(tmp_files)

        self.message_user(request, ngettext(
        '%d file downloaded',
        '%d files downloaded',
        submissions,
        ) % len(submissions), messages.SUCCESS)

        return zip_response
        
    download.short_description = "Download the selected files"

admin.site.register(Comment)
