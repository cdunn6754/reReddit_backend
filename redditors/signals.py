from django.db.models import signals, Sum
from django.dispatch import receiver

from redditors.models import User
from votes.models import CommentVote, PostVote

@receiver(signals.post_save, sender=CommentVote)
@receiver(signals.post_save, sender=PostVote)
def karma_on_comment_vote(sender, instance, **kwargs):
    """
    On a vote creation or update, make the appropriate change to user karma.
    
    TODO: Now I wish that I hadn't made the vote class abstract. I could
    get away with one aggregate query. Should investigate if migrating to a
    multi-table inheritance for votes would cause any problems.
    
    Alternatively I could probably come up with a more complex but
    efficient way to do this with incrementing for each vote change.
    This has become a little inefficient but it's a more difficult problem
    than it seems.
    
    Another idea that could make this easier is to recognize that reddit
    separates karma into comment and post karma, we could make the User
    model reflect that and then handle each separately here.
    """
    
    # Need the poster of the comment or vote.
    if sender == CommentVote:
        poster = instance.comment.poster
    elif sender == PostVote:
        poster = instance.post.poster
        
    comment_karma = CommentVote.objects.filter(
        comment__poster_id=poster.pk
    ).aggregate( Sum('vote_type'))["vote_type__sum"] or 0
    post_karma = PostVote.objects.filter(
        post__poster_id=poster.pk
    ).aggregate( Sum('vote_type') )["vote_type__sum"] or 0
    
    poster.karma = post_karma + comment_karma
    poster.save()
        
        
