from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.SubListView.as_view(), name='sub-list'),
    path('sub/<slug:title>/', views.SubDetailView.as_view(), name='sub-detail'),
    path('sub/<slug:title>/subscribe/',
         views.SubredditSubscribeView.as_view(),
         name='subreddit-subscribe'),
    path('sub/<slug:title>/post/',
         views.SubPostView.as_view(),
         name='sub-post'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
