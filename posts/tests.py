from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from redditors.models import User, UserSubMembership
from subs.models import Sub

class PostTests(APITestCase):
    def setUp(self):
        client = APIClient()
        # We will need to set up a subReddit for the posts and 
        # it's hyperlink
        self.sub = Sub.objects.create(
            title='test Sub'
        )
        res = client.get(reverse('sub-list'))
        self.sub_hyperlink = res.data[0]['url']
        
        # We will need a user created
        self.username = 'test_username'
        self.email = 'test@gmail.com'
        self.password = 'test_password'
        # create user with an api request
        create_user_data = {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            }
        create_user_url = reverse('user-create')
        client.post(create_user_url, create_user_data)
        self.login_test_user()
                
    def login_test_user(self):
        client = APIClient()
        login_user_data = {
            'username': self.username,
            'password': self.password
            }
        login_user_url = reverse('user-login')
        login_res = client.post(login_user_url, login_user_data)
        self.token = login_res.data["token"]
        
    def test_create_post_no_member(self):
        """
        Try to create a post to a sub to which the user is not subsribed
        """
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION="Token {}".format(self.token))
        create_post_url = reverse('post-list')
        create_post_data = {
            'title' : 'test post title',
            'body' : 'test post body',
            'sub': self.sub_hyperlink
        }
        res = c.post(create_post_url,create_post_data)
        assert(res.status_code == 400)
        expected_message = "You must be a member of the subreddit to post here."
        assert(expected_message in str(res.data))

    def test_create_post_member(self):
        """
        Try to create a post to a sub to which the user is subscribed
        """
        # prepare client with user token header (is already logged in)
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION="Token {}".format(self.token))
        
        # sign user up as member of sub
        user = User.objects.get(username="test_username")
        UserSubMembership.objects.create(user=user, sub=self.sub)
        
        # again submit POST request to create a post on subreddit
        create_post_url = reverse('post-list')
        create_post_data = {
            'title' : 'test post title',
            'body' : 'test post body',
            'sub': self.sub_hyperlink
        }
        res = c.post(create_post_url,create_post_data)
        assert (res.status_code == 201)
        
        
        