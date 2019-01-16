from django.core.management.base import CommandError
from votes.management.commands._base_vote_command import VoteSeedCommandBase
import random

from votes.factory import CommentVoteFactory
from redditors.models import User
from comments.models import Comment
    
class Command(VoteSeedCommandBase):
    help="Adds fake comment votes to the database"
    
    def handle(self, *args, **options):
        n_votes = options['number']
        vote_ratio = options['vote_ratio']

        # Designed assuming relatively large batches of votes are made
        # just grab them all
        comments = list(Comment.objects.all())
        users = list(User.objects.all())
        
        out = "Creating {} new comment votes with a {} upvote ratio".format(
            n_votes,
            vote_ratio
        )
        self.stdout.write(out)
        for _ in range(n_votes):
            comment = random.choice(comments)
            user = random.choice(users)
            comment_vote = CommentVoteFactory.create(
                user=user,
                comment=comment,
                vote_ratio=vote_ratio
            )
            self.stdout.write("\t-- Voter: {}, Vote: {}".format(
                comment_vote.user,
                comment_vote.vote_type
            ))
