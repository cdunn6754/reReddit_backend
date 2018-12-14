from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from redditors.models import User
from posts.models import Post

class Comment(MPTTModel):
    created = models.DateTimeField(auto_now_add=True)
    
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    
    body = models.TextField()
    upvotes = models.IntegerField(default=0)
    
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
        return str(self.body)[:20]

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
