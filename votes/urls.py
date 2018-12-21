from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.CreateVoteView.as_view(), name='vote'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
