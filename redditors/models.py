from django.db import models
from django.contrib.auth.models import AbstractUser

from subs.models import Sub

class User(AbstractUser):
    karma = models.IntegerField(default=0)
    subs = models.ManyToManyField(
        Sub, through='UserSubMembership',
        related_name='members')
        
        
class UserSubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub = models.ForeignKey(Sub, on_delete=models.CASCADE)
    sign_up_date = models.DateTimeField(auto_now_add=True, blank=True)