from django.db import models

from redditors.models import User
from subs.models import Sub


class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    title = models.CharField(max_length=150, unique=True)
    body = models.TextField()
    
    subreddit = models.ForeignKey(Sub, on_delete=models.CASCADE)
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    voters = models.ManyToManyField(
        User,
        through='votes.PostVote',
        related_name='voted_posts',
    )
    
    @property
    def upvotes(self):
        """
        Just add up the votes vote_types.
        """
        return self.votes.all().aggregate(models.Sum('vote_type')).get(
            'vote_type__sum'
        ) or 0
    
    
    def __str__(self):
        return str(self.title)
