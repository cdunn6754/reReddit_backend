from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help="Populate the database with fake data."
    
    def handle(self,*args, **options):
        call_command('seed_users', number=100)
        call_command('seed_subreddits', number=50, members=10)
        call_command('seed_posts', number=100)
        call_command('seed_comments', number_roots=200)
        call_command('seed_comments', number_roots=50, number_children=50)
        call_command('seed_comments', number_children=50)
        call_command('seed_comments', number_children=50)
        call_command('seed_comments', number_children=50)
        call_command('seed_comments', number_children=50)
        call_command('seed_comment_votes', number=1000)
        call_command('seed_post_votes', number=1000)
