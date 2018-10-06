from django.db import models
from redditors.models import User


class Sub(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)    
    admins = models.ManyToManyField(User, related_name='sub')
    
