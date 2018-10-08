from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as drf_views

from . import views

urlpatterns = [
    path('', views.UserList.as_view(), name='user-list'),
    re_path('(?P<pk>[0-9]+)/', views.UserDetail.as_view(), name='user-detail'),
    path('login/', drf_views.obtain_auth_token),
    path('logout/', views.UserLogoutView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)