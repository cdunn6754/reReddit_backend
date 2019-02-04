from django.core.management.base import BaseCommand, CommandError
import random

from posts.factory import PostFactory
from redditors.models import User
from subs.models import Sub
    
class Command(BaseCommand):
    help="Adds fake comments to the database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            type=int,
            default=1,
            help='Number of posts to create'
        )
        
    def handle(self,*args, **options):
        n_posts = options['number']
        # grab a user for each post
        users = User.objects.all().prefetch_related('subs')
        
        out = "Creating {} new posts".format(n_posts)
        self.stdout.write(out)
        for _ in range(n_posts):
            # make sure to grab a user that has subreddit memberships
            poster = random.choice(users)
            while not len(poster.subs.all()):
                poster = random.choice(users)
            # assume you can only post in subreddits you are a member of
            subreddit = random.choice(poster.subs.all())
            post = PostFactory.create(poster=poster, subreddit=subreddit)
            self.stdout.write("\t-- Title: {} ...".format(post.title[0:10]))
