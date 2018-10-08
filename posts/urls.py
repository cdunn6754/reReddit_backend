from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    re_path('(?P<pk>[0-9]+)/', views.PostDetailView.as_view(), name='post-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)