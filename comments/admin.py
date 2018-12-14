from django.contrib import admin

from comments.models import Comment, CommentVote

admin.site.register(Comment)
admin.site.register(CommentVote)
