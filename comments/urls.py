from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.CommentListView.as_view(), name='comment-list'),
    path('post/<int:post_pk>/', views.PostCommentView.as_view(), name='comment-detail'),
    path('delete/<int:pk>/', views.DeleteCommentView.as_view(), name='comment-delete')
]

urlpatterns = format_suffix_patterns(urlpatterns)
