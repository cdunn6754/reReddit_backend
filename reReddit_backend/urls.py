"""reReddit_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
    'users': reverse('user-list', request=request, format=format),
    'subs': reverse('sub-list', request=request, format=format),
    'posts': reverse('post-list', request=request, format=format),
    'comments': reverse('comment-list', request=request, format=format),
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root),
    path('users/', include('redditors.urls')),
    path('subreddits/', include('subs.urls')),
    path('posts/', include('posts.urls')),
    path('comments/', include('comments.urls')),
    path('vote/', include('votes.urls')),
    path('search/', include('search.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
