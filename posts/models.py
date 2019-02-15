from django.db import models
from django_bleach.models import BleachField
from django.core.validators import MaxLengthValidator
from django.utils.translation import gettext as _
from django.utils import timezone

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
    
    # set default so that management command can overwrite
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    
    title = BleachField(
        validators=[MaxLengthValidator(
            150,
            message=_("The title can only be 150 characters in length.")
        )]
    )
    body = BleachField(blank=True)
    
    subreddit = models.ForeignKey(
        Sub,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    poster = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts"
    )
    
    voters = models.ManyToManyField(
        User,
        through='votes.PostVote',
        related_name='voted_posts',
    )
    
    # Reverse FK to Comment related_name="comments"
    
    @property
    def upvotes(self):
        """
        Just add up the prefetched votes vote_types.
        """
        return sum([vote.vote_type for vote in self.votes.all()])
    
    
    def __str__(self):
        return str(self.title)
