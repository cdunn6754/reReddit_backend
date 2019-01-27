from django.test import TestCase
from django.db import transaction
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse

from subs.models import Sub
from redditors.models import User, UserSubMembership


# Create your tests here.
class SubredditSubscriptionTests(APITestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create(
            username="test_user",
            email="test@gmail.com",
            password="testpassword"
        )
        self.user_pk = self.user.pk
        
        # create a subreddit
        self.subreddit_title = "test_subreddit"
        self.subreddit = Sub.objects.create(
            title=self.subreddit_title,
        )
        self.subreddit_pk = self.subreddit.pk
        
        self.subscribe_url = reverse(
            'subreddit-subscribe',
            kwargs = {"title": self.subreddit_title}
        )
        
        # some utility stuff
        self.sub_data = {"action": "sub"}
        self.unsub_data = {"action": "unsub"}
        
        # We need an authenticated user
        self.client.force_login(self.user)
        
    
    def test_subscribe_to_subreddit(self):

        # should not be any subscriptions yet
        self.assertEqual(UserSubMembership.objects.count(), 0)
        # subscribe
        response = self.client.post(self.subscribe_url, self.sub_data)
        self.assertEqual(UserSubMembership.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user_pk)
        self.assertEqual(response.data["sub"]["pk"], self.subreddit_pk)
        
        # test unsubscribe
        response = self.client.post(self.subscribe_url, self.unsub_data)
        self.assertEqual(UserSubMembership.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_subscribe_to_non_subreddit(self):
        """
        Subscribing to a non-existant subreddit should raise an error
        """
        non_existant_url = reverse(
            'subreddit-subscribe',
            kwargs={"title": "doesntexist"}
        )
        response = self.client.post(non_existant_url, self.sub_data)
        self.assertEqual(UserSubMembership.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resubscribe(self):
        """
        Trying to subscribe to a subreddit to which you are already subscribed
        raises an error
        """
        response = self.client.post(self.subscribe_url, self.sub_data)
        self.assertEqual(UserSubMembership.objects.count(), 1)
        with transaction.atomic():
            response = self.client.post(self.subscribe_url, self.sub_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserSubMembership.objects.count(), 1)
