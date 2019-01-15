from django.core.management.base import BaseCommand, CommandError
import random

from comments.factory import CommentFactory
from redditors.models import User
from posts.models import Post
    
class Command(BaseCommand):
    help="Adds fake comments to the database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            type=int,
            default=1,
            help='Number of comments to create'
        )
        
    def handle(self,*args, **options):
        n_comments = options['number']
        # grab a user for each comment
        users = User.objects.all()
        posts = Post.objects.all()
        
        out = "Creating {} new comments".format(n_comments)
        self.stdout.write(out)
        for _ in range(n_comments):
            poster = random.choice(users)
            post = random.choice(posts)
            comment = CommentFactory.create(poster=poster, post=post)
            self.stdout.write("\t-- Body: {} ...".format(comment.body[0:10]))
