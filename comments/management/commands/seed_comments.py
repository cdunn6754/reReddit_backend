from django.core.management.base import BaseCommand, CommandError
import random

from comments.factory import CommentFactory
from comments.models import Comment
from redditors.models import User
from posts.models import Post
    
class Command(BaseCommand):
    help="Adds fake comments to the database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number_roots',
            '-r',
            type=int,
            default=1,
            help='Number of root comments to create'
        )
        
        parser.add_argument(
            '--number_children',
            '-c',
            type=int,
            default=1,
            help='Number of child comments to create'
        )
        
    def handle(self,*args, **options):
        n_roots = options['number_roots']
        n_children = options['number_children']

        users = User.objects.all()
        posts = Post.objects.all()
        comments = Comment.objects.all()
        
        if n_roots:
            out = "Creating {} new root comments".format(n_roots)
            self.stdout.write(out)
            for _ in range(n_roots):
                poster = random.choice(users)
                post = random.choice(posts)
                comment = CommentFactory.create(poster=poster, post=post)
                self.stdout.write("\t-- Body: {} ...".format(comment.body[0:10]))
                
        if n_children:
            out = "Creating {} new child comments".format(n_children)
            self.stdout.write(out)
            for _ in range(n_children):
                poster = random.choice(users)
                parent = random.choice(comments)
                comment = CommentFactory.create(poster=poster, parent=parent)
                self.stdout.write("\t-- Body: {} ...".format(comment.body[0:10]))
