from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from posts.models import Post
from subs.models import Sub
from redditors.models import User

class SearchView(APIView):
    """
    Very simple search view, takes a single POST parameter and
    searches database for post, sureddit and users that contain
    that text. It then returns a serialized list of for each.
    In the case of Posts the pks are returned, for Subreddits and users
    the title and username are returned.
    """
    http_method_names=['post']
    
    def post(self, request, format=None, **kwargs):

        search_term = request.data['search_term']
        
        posts = Post.objects.filter(title__icontains=search_term)
        users = User.objects.filter(username__icontains=search_term)
        subreddits = Sub.objects.filter(title__icontains=search_term)
        
        post_pks = [post.pk for post in posts]
        user_usernames = [user.username for user in users]
        subreddit_titles = [subreddit.title for subreddit in subreddits]

        data = {
            'post_pks': post_pks,
            'user_usernames': user_usernames,
            'subreddit_titles': subreddit_titles,
        }
        
        return Response(data=data)
