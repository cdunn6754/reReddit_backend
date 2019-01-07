from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from posts.models import Post
from posts.serializers import PostSerializer
from subs.models import Sub
from subs.serializers import SubSerializer
from redditors.models import User
from redditors.serializers import UserSerializer


class SearchView(APIView):
    """
    Very simple search view, takes a single GET query param and
    searches database for post, sureddit and users that contain
    that text. It then returns a serialized list of for each.
    In the case of Posts the pks are returned, for Subreddits and users
    the title and username are returned.
    """
    http_method_names=['get']
    
    def get(self, request, format=None, **kwargs):

        search_term = request.GET.get('q', '')
        
        posts = Post.objects.filter(title__icontains=search_term)
        users = User.objects.filter(username__icontains=search_term)
        subreddits = Sub.objects.filter(title__icontains=search_term)
        
        post_pks = PostSerializer(posts, many=True)
        user_usernames = UserSerializer(
            users,
            many=True,
            context={'request': request}
        )
        subreddit_titles = SubSerializer(
            subreddits,
            many=True,
            context={'request': request},
        )

        data = {
            'post_pks': post_pks.data,
            'user_usernames': user_usernames.data,
            'subreddit_titles': subreddit_titles.data,
        }
        
        return Response(data=data)
