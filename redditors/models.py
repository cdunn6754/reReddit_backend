from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

from subs.models import Sub

class User(AbstractUser):
    karma = models.IntegerField(default=0)
    subs = models.ManyToManyField(
        Sub,
        through='UserSubMembership',
        related_name='members',
        
    )
    #moderated_subs ManyToManyField, related_name="moderated_subs"

class UserSubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub = models.ForeignKey(Sub, on_delete=models.CASCADE)
    sign_up_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'sub')