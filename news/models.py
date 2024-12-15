from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField(blank=False)
    image = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=100)
    pub_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
