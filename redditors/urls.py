from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user-list'),
    path('login/', obtain_auth_token),
    path('logout/', views.UserLogoutView.as_view()),
    path('create/', views.CreateUserView.as_view()),
    path('user/<slug:username>/', views.UserDetailView.as_view(), name='user-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)