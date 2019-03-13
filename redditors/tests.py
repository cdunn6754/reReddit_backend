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
from comments.models import Comment

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
        self.post = Post.objects.create(**self.post_data)
        self.comment_data = {
            "poster": self.user,
            "post": self.post,
            "body":"test comment 1"
        }
        self.comment = Comment.objects.create(**self.comment_data)
        self.comment_data_2 = {
            "poster": self.user,
            "post": self.post,
            "parent": self.comment,
            "body": "test comment 2"
        }
        self.comment_2 = Comment.objects.create(**self.comment_data_2)
        
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
        
    def test_nested_comments(self):
        """
            The profile information should include nested comments by this user.
            and those comments contain nested post information
        """
        response = self.client.get(self.user_profile_url)
        self.assertContains(response, self.comment_data["body"])
        self.assertContains(response, self.comment_data_2["body"])
        res_comment_data = response.data["comments"]
        
        comment_1_data = next(
            c for c in res_comment_data if c["pk"] == self.comment.pk
        )
        comment_2_data = next(
            c for c in res_comment_data if c["pk"] == self.comment_2.pk
        )
        
        self.assertEqual(comment_1_data["post"]["pk"], self.post.pk)
        self.assertEqual(comment_2_data["post"]["pk"], self.post.pk)
        self.assertEqual(comment_1_data["post"]["poster"], self.user.pk)
        self.assertEqual(comment_2_data["post"]["poster"], self.user.pk)

    
    def test_user_profile_name_error(self):
        """When given a non-existant username, returns a 404"""
        response = self.client.get(reverse(
            'user-profile',
            kwargs={'username': 'not_a_name'}
        ))
        self.assertContains(response, "Not found", status_code=404)
        
    def test_profile_post_not_allowed(self):
        """This endpoint is read only, no posts, results in 403"""
        response = self.client.post(
            self.user_profile_url,
            {"username": "dummy_username"}
        )
        self.assertEqual(response.status_code, 403)
        
class SeedUsersCommandTests(TestCase):
    
    def test_create_users(self):
        """Can create useres with the command"""
        out = StringIO()
        call_command('seed_users', number=10, stdout=out)
        expected_out = "Creating 10 new users"
        self.assertIn(expected_out, out.getvalue())
        self.assertEqual(User.objects.count(), 10)
