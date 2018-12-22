from django.contrib import admin

from .models import CommentVote, PostVote

admin.site.register(CommentVote)
admin.site.register(PostVote)
