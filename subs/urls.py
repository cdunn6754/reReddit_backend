from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('list/', views.SubList.as_view(), name='sub-list'),
    re_path('(?P<pk>[0-9]+)/', views.SubDetail.as_view(), name='sub-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)