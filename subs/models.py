from django.db import models
from django.core.exceptions import  FieldError

class Sub(models.Model):
    protected_subreddit_titles = [
        'Popular',
        'New',
        'Hot',
        'Home',
    ]
    
    created = models.DateTimeField(auto_now_add=True)
    title = models.SlugField(max_length=40, unique=True)
    description = models.CharField(max_length=1000, blank=True)
    
    moderators = models.ManyToManyField(
        'redditors.User',
        related_name='moderated_subs')
        
    #ManyToManyField to User, related_name="members"
    
    def __str__(self):
        return "subReddit: {}".format(self.title)
        
    def save(self, *args, **kwargs):
        """
        Prevent creation of subreddits that use names
        needed for the psuedo subreddits
        """
        if self.title.title() in self.protected_subreddit_titles:
            message = "The subreddit title '{}' is reserved".format(self.title)
            raise FieldError(message)
        else:
            super().save(*args, **kwargs)
        
