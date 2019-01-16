from django.db import models, IntegrityError

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
    
    class Meta:
        abstract = True

class CommentVote(VoteAbstractBase):

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    
    def __str__(self):
        return "Comment: {}; Vote: {}".format(self.comment, self.vote_type)
        
    def save(self, *args, **kwargs):
        """
        Sometimes, e.g. for the seed_comment_votes management command, the
        creation of a comment vote will run into an IntegrityError when
        created for a user/comment pair that already exists. This doesn't
        occur in general because of serializer validation. When it
        does happen we want it to fail silently and just update the vote_type.
        """
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            vote_data = {
                'user': self.user,
                'comment':self.comment,
            }
            CommentVote.objects.update_or_create(
                **vote_data,
                defaults = {'vote_type': self.vote_type},
            )
            
    
    class Meta:
        unique_together = ('comment', 'user')
        
class PostVote(VoteAbstractBase):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_votes')
    
    def __str__(self):
        return "Post: {}; Vote: {}".format(self.post, self.vote_type)
        
    def save(self, *args, **kwargs):
        """
        Sometimes, e.g. for the seed_post_votes management command, the
        creation of a post vote will run into an IntegrityError when
        created for a user/post pair that already exists. This doesn't
        occur in general because of serializer validation. When it
        does happen we want it to fail silently and just update the vote_type.
        """
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            vote_data = {
                'user': self.user,
                'post':self.post,
            }
            PostVote.objects.update_or_create(
                **vote_data,
                defaults = {'vote_type': self.vote_type},
            )
    
    class Meta:
        unique_together = ('post', 'user')
