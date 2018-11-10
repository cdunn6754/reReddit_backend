from django.shortcuts import render
from rest_framework import generics, permissions, renderers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import User
from .serializers import UserSerializer, CreateUserSerializer
from subs.serializers import SubSerializer

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
            
class UserLoginView(ObtainAuthToken):
        
        def post(self, request, *args, **kwargs):
            serializer = self.serializer_class(data=request.data,
                                               context={'request':request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            subs = SubSerializer(user.subs.all(),
                                 many=True,
                                 context={'request':request})
            moderated_subs = SubSerializer(user.subs.all(),
                                           many=True,
                                           context={'request':request})
            return Response({
                'token': token.key,
                'username': user.username,
                'subs': subs.data,
                'moderated_subs': moderated_subs.data
            })
    


