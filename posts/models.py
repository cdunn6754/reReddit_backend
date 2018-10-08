from django.db import models

from redditors.models import User
from subs.models import Sub


class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    title = models.CharField(max_length=150)
    body = models.TextField()
    upvotes = models.IntegerField(default=0)
    
    sub = models.OneToOneField(Sub, on_delete=models.CASCADE)
    poster = models.OneToOneField(User, on_delete=models.CASCADE)
