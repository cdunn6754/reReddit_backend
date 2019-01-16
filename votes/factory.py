import factory
import random

from votes.models import CommentVote, PostVote

class CommentVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentVote
        
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        vote_ratio = kwargs.pop('vote_ratio', 0.75)
        kwargs['vote_type'] = (CommentVote.UPVOTE
            if random.random() <= vote_ratio
            else CommentVote.DOWNVOTE
        )
        return super()._create(model_class, *args, **kwargs)
        
class PostVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostVote
        
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        vote_ratio = kwargs.pop('vote_ratio', 0.75)
        kwargs['vote_type'] = (PostVote.UPVOTE
            if random.random() <= vote_ratio
            else PostVote.DOWNVOTE
        )
        return super()._create(model_class, *args, **kwargs)
        
