from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from redditors.models import User
from posts.models import Post

class Comment(MPTTModel):
    created = models.DateTimeField(auto_now_add=True)
    
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    
    body = models.TextField()

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
        through='CommentVote',
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

class CommentVote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    NO_VOTE = 0
    VOTE_CHOICES = (
        (UPVOTE, 'upvote'),
        (DOWNVOTE, 'downvote'),
        (NO_VOTE, 'no_vote'),
    )
    
    vote_type = models.IntegerField(
        choices=VOTE_CHOICES,
        default=NO_VOTE,
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('comment', 'user')
