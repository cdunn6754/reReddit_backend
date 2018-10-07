from django.db import models
from redditors.models import User


class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500, blank=True)
    admins = models.ManyToManyField(User, related_name='sub')
    
