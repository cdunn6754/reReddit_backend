from django.test import TestCase, Client
from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.core.management import call_command
from io import StringIO
from rest_framework.authtoken.models import Token

from redditors.models import User, UserSubMembership
from subs.models import Sub
from posts.models import Post
from comments.models import Comment

class UserORMTests(TestCase):
    """Tests of user creation within django, i.e. no client requests"""
    def setUp(self):
        self.user_data = {
            "username": "testUsername",
            'email': "test@gmail.com",
            'password': "testPassword"
        }

        self.user = User.objects.create(**self.user_data)

    def test_duplicate_username(self):
        """throw error for duplicated username"""
        user_data_2 = {
            "username": "testUsername",
            "email": "test2@gmail.com",
            "password": "testPassword2"
        }

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.user_2 = User.objects.create(**user_data_2)


        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_email(self):
        """throw error for duplicated email"""
        user_data_2 = {
            "username": "testUsername2",
            "email": "test@gmail.com",
            "password": "testPassword2"
        }

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.user_2 = User.objects.create(**user_data_2)

        self.assertEqual(User.objects.count(), 1)

class UserRequestTest(APITestCase):
    """Test user functionality through client requests"""
    def setUp(self):
        self.user_data = {
            'username': "testUsername",
            'email': "testUser@gmail.com",
            'password': "testPassword"
        }

    def test_create_user(self):
        """Can create a user with a client request"""
        create_url = reverse('user-create')
        response = self.client.post(create_url, self.user_data)
        self.assertContains(
            response,
            self.user_data['username'],
            status_code=201
        )
        self.assertEqual(User.objects.count(), 1)
        # The user is not logged in automatically
        self.assertEqual(Token.objects.count(), 0)

    def test_user_login_logout(self):
        """A user that has been created can login and logout"""
        # Create a user first
        create_url = reverse('user-create')
        self.client.post(create_url, self.user_data)
        # then login
        login_url = reverse('user-login')
        credentials = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(login_url, credentials)
        self.assertContains(response, self.user_data['username'])
        self.assertEqual(Token.objects.count(), 1)
        # # then logout
        # logout_url = reverse('user-logout')
        # response = self.client.post(
        #     logout_url,
        #     {},
        #     Authorization="Token {}".format(response.data['token'])
        # )
        # import pdb; pdb.set_trace()
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(Token.objects.count(), 0)

    def test_non_user_login(self):
        """Can't login without a user in the database"""
        login_url = reverse('user-login')
        credentials = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(login_url, credentials)
        self.assertContains(
            response,
            "Unable to log in with provided credentials.",
            status_code=400
        )

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
