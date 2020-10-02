import shutil
from pathlib import Path

from django.contrib import admin, messages
from django.utils.translation import ngettext

from .download import get_zip
from .models import Comment, Submission
from .dubbings import MakeDubbingAudioFiles, DubError
from .subtitles import MakeSubImageFiles


# Register your models here.
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    passdate_hierarchy = 'scraped_time'
    list_display = (
        'sub_id', 'subreddit', 'score', 
        'text_len', 'sub_len', 'created_time', 'title'
        )
    ordering = ('-created_time',)
    actions = ['download', 'make_dub', 'make_sub']

    def download(self, request, submissions):

        self.message_user(request, ngettext(
            '%d file downloaded',
            '%d files downloaded',
            submissions,
            ) % len(submissions), messages.SUCCESS)

        return get_zip(request, submissions)

    def make_dub(self, request, submissions):

        try:
            dub = MakeDubbingAudioFiles(submissions)
            zip_file = dub.return_zip()

            self.message_user(
                request, 
                ngettext(
                    '%d file downloaded',
                    '%d files downloaded',
                    submissions,
                    ) % len(submissions),
                messages.SUCCESS
                )
            return zip_file
        
        except DubError:
            self.message_user(
                request, 
                'Error occured while generating a dub zip.',
                messages.ERROR
            )
        
        

    def make_sub(self, request, submissions):
    
        self.message_user(request, ngettext(
            '%d file downloaded',
            '%d files downloaded',
            submissions,
            ) % len(submissions), messages.SUCCESS)
        
        sub = MakeSubImageFiles(submissions)
        zip_file = sub.return_zip()
        return zip_file

        
    download.short_description = "Download the selected files"

admin.site.register(Comment)
