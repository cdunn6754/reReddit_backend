from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help="Adds fake subreddits to the database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            help='Number of subreddits to create'
        )
    
    def handle(self,*args, **options):
        for _ in range(options['number']):
