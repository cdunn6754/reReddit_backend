from django.test import TestCase, Client
from django.db import transaction
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.core.management import call_command
from io import StringIO

from redditors.models import User, UserSubMembership
from subs.models import Sub
from posts.models import Post

# Create your tests here.

class UserProfileTest(APITestCase):
    """
    Can get a use profile.
    """
    def setUp(self):
        self.user_data = {
            "username": "testUsername",
            'email': "test@gmail.com",
            'password': "testPassword"
        }
        self.user = User.objects.create(**self.user_data)
        self.subreddit = Sub.objects.create(title="test subreddit")
        UserSubMembership.objects.create(user=self.user, sub=self.subreddit)
        self.post_data = {
            "poster": self.user,
            "subreddit": self.subreddit,
            "title": "test post title",
            "body": "test post body"
        }
        Post.objects.create(**self.post_data)
        self.user_profile_url = reverse(
            'user-profile',
            kwargs={'username': self.user_data["username"]})
        
    def test_get_user_profile(self):
        response = self.client.get(self.user_profile_url)
        self.assertContains(response, self.user_data["username"])
        self.assertContains(response, self.post_data["body"])
        self.assertNotContains(response, self.user_data["password"])
        self.assertNotContains(response, self.user_data["email"])
        self.assertContains(response, "cake_day")
        self.assertContains(response, "karma")
        
        
        
        
