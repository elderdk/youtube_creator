from django.db import models


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
    dub_text = models.TextField(blank=True)
    sub_len = models.IntegerField(default=0, blank=True)
    sub_bg_image = models.CharField(max_length=300, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.sub_len = len(self.dub_text)
        super().save(*args, **kwargs)


class Comment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    body = models.TextField()
