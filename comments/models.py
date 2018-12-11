from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from redditors.models import User
from posts.models import Post

class Comment(MPTTModel):
    created = models.DateTimeField(auto_now_add=True)
    
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    
    body = models.TextField()
    upvotes = models.IntegerField(default=0)
    
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True,
        blank=True, related_name='children'
    )
    
    def __str__(self):
        return str(self.body)[:20]
