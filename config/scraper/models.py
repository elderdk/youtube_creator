from django.db import models

# Create your models here.
class Submission(models.Model):
    title = models.CharField(max_length = 500)
    author = models.CharField(max_length = 30)
    sub_id = models.CharField(max_length = 10)
    permalink = models.CharField(max_length= 200)
    selftext = models.TextField()
    created_time = models.DateTimeField()
    scraped_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)