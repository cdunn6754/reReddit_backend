from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django_bleach.models import BleachField
from django.utils import timezone

from redditors.models import User
from posts.models import Post

class Comment(MPTTModel):
    # set default so that management command can overwrite
    created = models.DateTimeField(default=timezone.now)
    
    poster = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        related_name="comments"
    )
    
    body = BleachField()
    deleted = models.BooleanField(default=False)

    @property
    def upvotes(self):
        """
        This doesn't need it's own db field. Can be calculated
        based on the m2m through table CommentVote. This will
        follow the reverse relation to CommentVote and sum votes.
        They are +1 for upvote, -1 for downvote and 0 for no vote.
        """
        return self.votes.all().aggregate(models.Sum('vote_type')).get(
            'vote_type__sum'
        ) or 0
    
    # Every user only gets one vote per comment
    voters = models.ManyToManyField(
        User,
        through='votes.CommentVote',
        related_name='voted_comments'
    )
    
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    
    def __str__(self):
        return str("pk: {}, {}".format(self.pk, self.body[:20]))
