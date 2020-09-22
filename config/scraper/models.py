from django.db import models
from datetime import datetime
from django.utils import timezone
import praw

# Create your models here.
class Submission(models.Model):
    subreddit = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=30)
    sub_id = models.CharField(max_length=7)
    url = models.CharField(max_length=200)
    score = models.IntegerField()
    selftext = models.TextField()
    text_len = models.IntegerField()
    created_time = models.DateTimeField()
    scraped_time = models.DateTimeField(auto_now_add=True)
    # make charfield placeholders called "st_path" and "tt_path" for soure and target path, to be updated upon creation and upload

    def __str__(self):
        return self.title

class Comment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    body = models.TextField()