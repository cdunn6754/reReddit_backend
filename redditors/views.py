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
    
    # It is more useful in the frontend to have the actual sub
    # information than just the hyperlinks
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        subs = SubSerializer(instance.subs.all(),
                             many=True,
                             context={'request':request})
        moderated_subs = SubSerializer(instance.moderated_subs.all(),
                                       many=True,
                                       context={'request':request})
        return Response({**serializer.data, 'subs':subs.data, 'moderated_subs':moderated_subs.data})
    
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
            moderated_subs = SubSerializer(user.moderated_subs.all(),
                                           many=True,
                                           context={'request':request})
            return Response({
                'token': token.key,
                'username': user.username,
                'pk': user.pk,
                'subs': subs.data,
                'moderated_subs': moderated_subs.data

            })
    
