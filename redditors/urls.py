from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('list', views.UserList.as_view(), name='user-list'),
    re_path('(?P<pk>[0-9]+)/', views.UserDetail.as_view(), name='user-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)