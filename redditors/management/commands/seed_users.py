from django.core.management.base import BaseCommand, CommandError
import random

from redditors.factory import UserFactory
    
class Command(BaseCommand):
    help="Adds fake users to the database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            default=1,
            help='Number of users to create'
        )
        
    def handle(self,*args, **options):
        n_users = options['number']
        
        out = "Creating {} new users".format(n_users)
        self.stdout.write(out)
        for _ in range(n_users):
            user = UserFactory.create()
