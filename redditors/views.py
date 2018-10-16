from django.shortcuts import render
from rest_framework import generics, permissions, renderers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

from .models import User
from .serializers import UserSerializer, CreateUserSerializer

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer    
    
class UserLogoutView(APIView):
        permission_classes = [IsAuthenticated]

        def post(self, request, *args, **kwargs):
            try:
                request.user.auth_token.delete()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
    


