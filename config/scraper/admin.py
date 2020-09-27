import shutil
from pathlib import Path

from django.contrib import admin, messages
from django.utils.translation import ngettext

from .download import get_zip
from .models import Comment, Submission
from .dub_maker import MakeDub
from .sub_maker import MakeSub


# Register your models here.
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    passdate_hierarchy = 'scraped_time'
    list_display = (
        'sub_id', 'subreddit', 'score', 
        'text_len', 'created_time', 'title'
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

        self.message_user(request, ngettext(
            '%d file downloaded',
            '%d files downloaded',
            submissions,
            ) % len(submissions), messages.SUCCESS)
        
        dub = MakeDub(submissions)
        return dub.get_zip()

    def make_sub(self, request, submissions):
    
        self.message_user(request, ngettext(
            '%d file downloaded',
            '%d files downloaded',
            submissions,
            ) % len(submissions), messages.SUCCESS)
        
        sub = MakeSub(submissions)
        return sub.get_zip()

        
    download.short_description = "Download the selected files"

admin.site.register(Comment)
