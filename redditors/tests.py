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
    Can get a user profile.
    """
    def setUp(self):
        self.user_data = {
            "username": "testUsername",
            'email': "test@gmail.com",
            'password': "testPassword"
        }
        self.user_data_2 = {
            "username": "testUsername2",
            'email': "test2@gmail.com",
            'password': "testPassword2"
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
        """
        A request to the user profile view returns the expected information
        and it doesn't contain information about the other user
        """
        response = self.client.get(self.user_profile_url)
        self.assertContains(response, self.user_data["username"])
        self.assertContains(response, self.post_data["body"])
        self.assertNotContains(response, self.user_data["password"])
        self.assertNotContains(response, self.user_data["email"])
        self.assertContains(response, "cake_day")
        self.assertContains(response, "karma")
        
        self.assertNotContains(response, self.user_data_2["username"])
        self.assertNotContains(response, self.user_data_2["email"])
        self.assertNotContains(response, self.user_data_2["password"])
    
    def test_user_profile_name_error(self):
        """When given a non-existant username, returns a reasonable error"""
        response = self.client.get(reverse(
            'user-profile',
            kwargs={'username': 'not_a_name'}
        ))
        self.assertContains(response, "Not found", status_code=404)
        
        
        
