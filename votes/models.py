from django.db import models

from comments.models import Comment
from posts.models import Post
from redditors.models import User

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
        
class PostVote(models.Model):
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
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return "Post: {}; Vote: {}".format(self.post, self.vote_type)
    
    class Meta:
        unique_together = ('post', 'user')
