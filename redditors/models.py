from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

from subs.models import Sub

class User(AbstractUser):
    karma = models.IntegerField(default=0)
    subs = models.ManyToManyField(
        Sub,
        through='UserSubMembership',
        related_name='members',
        
    )
    #ManyToManyField on Subreddit, related_name="moderated_subs"
    #ManyToManyField for votes on Comment, related_name="voted_comments"
    #ManyToManyField for votes on Post, related_name="voted_posts"
    # Reverse FK for user votes on PostVote, related_name="post_votes"
    # Reverse FK for user votes on CommentVote, related_name="comment_votes"
    # Reverse FK to Comment related_name="comments"
    # Reverse FK to Post related_name="posts"
    
class UserSubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub = models.ForeignKey(Sub, on_delete=models.CASCADE)
    sign_up_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'sub')
