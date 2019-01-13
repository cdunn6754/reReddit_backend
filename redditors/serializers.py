from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from rest_framework.validators  import UniqueValidator

from .models import User, UserSubMembership
from subs.models import Sub

class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    subs = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    
    moderated_subs = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    
    class Meta:
        model = User
        fields = ('pk', 'karma', 'username', 'subs', 'moderated_subs',)
        
class CreateUserSerializer(serializers.ModelSerializer):
    
    username = serializers.SlugField(
        max_length=128,
        min_length=4,
        required=True,
        help_text=_(
            'Required, 4-128 characters, only letters, numbers, underscores and hyphens.'
            ),
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This username is already in use."
                )
            ]
    )

    password = serializers.CharField(
        max_length=128, min_length=6, write_only=True, required=True,
        help_text=_('Required, 6-128 characters')
        )
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
                    queryset=User.objects.all(),
                    message="This email is already in use."
                    )]
    )
    
    subs = serializers.HyperlinkedRelatedField(
        required=False,
        many=True,
        queryset = Sub.objects.all(),
        view_name="sub-detail"
        )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'subs']
        
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
            )
        user.set_password(validated_data['password'])
        user.save()
        
        if validated_data.get('subs'):
            for sub in validated_data['subs']:
                UserSubMembership.objects.get_or_create(user=user, sub=sub)
        
        return user
    
    
    
    
    
    
