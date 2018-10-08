from django.db import models
from django.core.exceptions import  ValidationError


from redditors.models import User


class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500, blank=True)
    
    members = models.ManyToManyField(User, related_name='subs')
    moderators = models.ManyToManyField(User, related_name='moderated_subs')
    
    def __str__(self):
        return "subReddit: {}".format(self.title)
    
    
    def makeModeratorsMembers(self):
        moderators = self.moderators.all()
        for moderator in moderators:
            if not moderator in self.members.all():
                self.members.add(moderator)                                
    
    def save(self, *args, **kwargs):
        """
        Make the moderators members if they aren't already
        Also be sure that there is at least one moderator
        """                
        super().save(*args,**kwargs)            
        self.makeModeratorsMembers()                
        super().save(*args,**kwargs)
        
        
        
    
