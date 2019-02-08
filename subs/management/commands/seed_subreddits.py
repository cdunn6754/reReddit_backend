from django.core.management.base import BaseCommand, CommandError
import random

from subs.factory import SubredditFactory, UserSubredditMembershipFactory
from redditors.models import User
    
class Command(BaseCommand):
    help="Adds fake subreddits to the database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            type=int,
            default=1,
            help='Number of subreddits to create'
        )
        
        parser.add_argument(
            '--members',
            type=int,
            default=1,
            help='Number of user memberships to create per subreddit'
        )
        
    def handle(self,*args, **options):
        n_subreddits = options['number']
        n_members = options['members']
        
        users = list(User.objects.all())
        
        out = "Creating {} new subreddits with {} members each".format(
            n_subreddits,
            n_members,
        )
        self.stdout.write(out)
        for _ in range(n_subreddits):
            subreddit_users = random.sample(users, n_members)
            # just create the sub with a single moderator
            subreddit = SubredditFactory.create(moderators=(subreddit_users[0],))
            for user in subreddit_users:
                membership = UserSubredditMembershipFactory.create(
                    user=user,
                    sub=subreddit
                )
            self.stdout.write("\t-- Title: {} ...".format(subreddit.title))
