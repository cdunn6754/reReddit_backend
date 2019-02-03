from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from rest_framework.validators  import UniqueValidator

from .models import User, UserSubMembership
from subs.models import Sub

class UserSerializer(serializers.ModelSerializer):
    
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
        
class UserCreateSerializer(serializers.ModelSerializer):
    
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
        
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Currently only used to update user password and/or email.
    No email verification is currently included, other than
    a check for uniqueness. Whatever they change they must
    provide their current password in addition to being
    already otherwise authenticated.
    """

    current_password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        required=True,
        help_text=_('Required, 6-128 characters')
        )
        
    new_password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Sorry! This email is already in use."
            )
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'current_password', 'new_password']
        lookup_field = 'username'
        
    def update(self, instance, validated_data):
        try:
            user = self.context.get('request').user
        except:
            message = _("You must be logged in to make profile changes.")
            raise serializers.ValidationError(message)
            
        try:
            current_password = validated_data.pop('current_password')
        except KeyError:
            message = _("Please enter your current password.")
            raise serializers.ValidationError(message)
            
        if not user.check_password(current_password):
            message = _("Please enter your current password")
            raise serializers.ValidationError(message)
        
        if validated_data.get("new_password"):
            new_password = validated_data.pop("new_password")
            if new_password == current_password:
                message = _("Your new password can not be set the to the "
                "same value as your current password")
                raise serializers.ValidationError(message)
            user.set_password(new_password)
            
        if validated_data.get("email"):
            user.email = validated_data['email']
        print(validated_data.get("email"))
        user.save()
        
        return user
    

from comments.serializers import CommentSerializer
from posts.serializers import PostSerializer
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Provide the detail of a user, not for login but for profile pages.
    All information provied here will be publicly accessable.
    """
    subs = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    moderated_subs = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    cake_day = serializers.DateTimeField(
        source='date_joined'
    )
    comments = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'subs',
            'moderated_subs',
            'comments',
            'posts',
            'karma',
            'cake_day'
        )
        
    def get_comments(self, obj):
        serializer = CommentSerializer(
            obj.comments.all().order_by("-created"),
            many=True,
            context=self.context
        )
        return serializer.data
    def get_posts(self, obj):
        serializer = PostSerializer(
            obj.posts.all().order_by("-created"),
            many=True,
            context=self.context
        )
        return serializer.data
    
    
