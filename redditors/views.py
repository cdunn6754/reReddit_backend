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
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer
)
from subs.serializers import SubSerializer
from redditors.permissions import IsLoggedInOrReadOnly

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = ( IsLoggedInOrReadOnly, )
    lookup_field = 'username'
    
    def get_serializer_class(self):
        """
        Probably should be using a view set but for now
        just pick a serializer based on the http method.
        """
        if  self.request.method.lower() == "patch":
            return UserUpdateSerializer
        return UserSerializer
    
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    
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
            serializer = self.serializer_class(
                data=request.data,
                context={'request':request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            subs = SubSerializer(user.subs.all(),
                many=True,
                context={'request':request}
            )
            moderated_subs = SubSerializer(
                user.moderated_subs.all(),
                many=True,
                context={'request':request}
            )
            return Response({
                'token': token.key,
                'username': user.username,
                'pk': user.pk,
                'subs': subs.data,
                'moderated_subs': moderated_subs.data
            })
    
