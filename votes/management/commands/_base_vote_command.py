from django.core.management.base import BaseCommand, CommandError
import random

class VoteSeedCommandBase(BaseCommand):
    
    @staticmethod
    def ratio_checker(ratio):
        message = "The ratio argument must be a number between 0 and 1"
        try:
            ratio = float(ratio)
        except ValueError:
            raise CommandError(message)
        if ratio >= 0 and ratio <=1.0:
            return ratio
        else:
            raise CommandError(message)
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            type=int,
            default=1,
            help='Number of comment votes to create'
        )
        parser.add_argument(
            '--vote_ratio',
            '-r',
            type=self.ratio_checker,
            default=0.75,
            help=('Ratio of upvotes to downvotes to be randomly assigned, '
                'defaults to 0.75')
        )
