from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import  ValidationError
from django.dispatch import receiver


from redditors.models import User


class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500, blank=True)
    
    members = models.ManyToManyField(User, related_name='subs')
    moderators = models.ManyToManyField(User, related_name='moderated_subs')
    
    def __str__(self):
        return "subReddit: {}".format(self.title)

        
    
