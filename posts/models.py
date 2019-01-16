from django.db import models

from redditors.models import User
from subs.models import Sub

class PostVotesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('votes')

class Post(models.Model):
    # This is the default because it is not very common to
    # not need to calculate upvotes and that will result in
    # a lot of db hits if we don't prefetch the votes
    objects = PostVotesManager()
    
    objects_no_votes = models.Manager()
    
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
        Just add up the prefetched votes vote_types.
        """
        return sum([vote.vote_type for vote in self.votes.all()])
    
    
    def __str__(self):
        return str(self.title)
