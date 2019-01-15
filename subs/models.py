from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import  ValidationError
from django.dispatch import receiver

class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=500, blank=True)
    
    moderators = models.ManyToManyField(
        'redditors.User',
        related_name='moderated_subs')
        
    #ManyToManyField to User, related_name="members"
    
    def __str__(self):
        return "subReddit: {}".format(self.title)



        
    
