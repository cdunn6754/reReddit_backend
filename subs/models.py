from django.db import models
from redditors.models import User


class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500, blank=True)
    
    members = models.ManyToManyField(User)
    moderators = models.ManyToManyField(User, related_name='moderated_sub')
    
    def __str__(self):
        return "subReddit: {}".format(self.title)
    
    def save(self, *args, **kwargs):
        """
        Make the moderators members if they aren't already
        """
        moderators = self.moderators.all()
        for moderator in moderators:
            if not moderator in self.members.all():
                self.members.add(moderator)
        
        
    
