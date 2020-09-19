from django.contrib import admin
from .models import Submission

# Register your models here.
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    passdate_hierarchy = 'scraped_time'
    list_display = ('sub_id', 'scraped_time', 'title')