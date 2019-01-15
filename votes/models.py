from django.db import models

from comments.models import Comment
from posts.models import Post
from redditors.models import User

class VoteAbstractBase(models.Model):
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True

class CommentVote(VoteAbstractBase):

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    
    def __str__(self):
        return "Comment: {}; Vote: {}".format(self.comment, self.vote_type)
    
    class Meta:
        unique_together = ('comment', 'user')
        
class PostVote(VoteAbstractBase):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    
    def __str__(self):
        return "Post: {}; Vote: {}".format(self.post, self.vote_type)
    
    class Meta:
        unique_together = ('post', 'user')
