from django.core.management.base import CommandError
from votes.management.commands._base_vote_command import VoteSeedCommandBase
import random

from votes.factory import PostVoteFactory
from redditors.models import User
from posts.models import Post
    
class Command(VoteSeedCommandBase):
    help="Adds fake post votes to the database"
        
    def handle(self,*args, **options):
        n_votes = options['number']
        vote_ratio = options['vote_ratio']

        # Designed assuming relatively large batches of votes are made
        # just grab them all
        posts = list(Post.objects_no_votes.all())
        users = list(User.objects.all())
        
        out = "Creating {} new post votes with a {} upvote ratio".format(
            n_votes,
            vote_ratio
        )
        self.stdout.write(out)
        for _ in range(n_votes):
            post = random.choice(posts)
            user = random.choice(users)
            post_vote = PostVoteFactory.create(
                user=user,
                post=post,
                vote_ratio=vote_ratio
            )
            self.stdout.write("\t-- Voter: {}, Vote: {}".format(
                post_vote.user,
                post_vote.vote_type
            ))
