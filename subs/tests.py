from django.test import TestCase, Client
from django.db import transaction
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.core.management import call_command
from io import StringIO

from subs.models import Sub
from redditors.models import User, UserSubMembership


class SubredditTest(APITestCase):
    def setUp(self):
        # need two users
        self.user1 = User.objects.create(
            username="test_user1",
            email="test1@gmail.com",
            password="testpassword"
        )
        self.user2 = User.objects.create(
            username="test_user2",
            email="test2@gmail.com",
            password="testpassword"
        )
        
        self.sub_data = {
            "title": "test_subreddit_1",
            "description": "This is the test subreddit",
        }
        
        self.create_subreddit_url = reverse('sub-list')
        self.detail_subreddit_url = reverse(
            'sub-detail',
            kwargs={"title": self.sub_data["title"]}
        )

        self.client.force_login(self.user1)
        self.client2 = Client().force_login(self.user2)
        
    def test_authenticated_subreddit_creation(self):
        """
        We can create a subreddit as expected and
        the creator will be in the moderators and members
        list of the new subreddit
        """
        response = self.client.post(self.create_subreddit_url, self.sub_data)
        self.assertEqual(Sub.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(
            Sub.objects.get(title=self.sub_data["title"]).pk,
            response.data["moderators"]
        )
        self.assertIn(
            Sub.objects.get(title=self.sub_data["title"]).pk,
            response.data["members"]
        )
        
    def test_unauthenticated_subreddit_creation(self):
        """
        Must be authenticated to make a subreddit.
        this may change to a karma threshold in the future
        """
        self.client.logout()
        response = self.client.post(self.create_subreddit_url, self.sub_data)
        self.assertEqual(Sub.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_psuedo_subreddit_creation(self):
        """
        Psuedo subreddits are those like "new", "all" and "popular".
        They are not true subreddits as they can't be posted to.
        They are handled manually and users should not be able to
        create subreddits with those names
        """
        for pseudo_name in Sub.pseudo_subreddits.keys():
            sub_data = self.sub_data
            sub_data['title'] = pseudo_name
            response = self.client.post(self.create_subreddit_url, self.sub_data)
            self.assertEqual(Sub.objects.count(), 0)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertContains(
                response,
                "The subreddit title '{}' is reserved".format(pseudo_name.title()),
                status_code=400
            )
            
    def test_subreddit_detail_request(self):
        """
        The detail view will return a list of moderators and members pks.
        When first created they will only contain the creator's pk.
        """
        _ = self.client.post(self.create_subreddit_url, self.sub_data)
        response = self.client.get(self.detail_subreddit_url)
        self.assertIn(self.user1.pk, response.data["members"])
        self.assertIn(self.user1.pk, response.data["moderators"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
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
        
    def test_unauthenticated_subscribe(self):
        """
        A user needs to be authenticated before subscribing
        """
        self.client.logout()
        response = self.client.post(self.subscribe_url, self.sub_data)
        self.assertEqual(UserSubMembership.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        
class SeedSubredditCommandTests(TestCase):
    def setUp(self):
        # need some users
        out = StringIO()
        call_command('seed_users', number=5, stdout=out)
            
    def test_seed_subreddit(self):
        """
        the seed_subreddits command creates subreddits, given a number parameter
        """
        out = StringIO()
        call_command('seed_subreddits', number=10, stdout=out)
        expected_out = ("Creating 10 new subreddits with 1 members each")
        self.assertIn(expected_out, out.getvalue())
        self.assertEqual(Sub.objects.count(), 10)
            
    def test_seed_subreddit_many_users(self):
        """
        the command can also add a variable number of users to each subreddit
        upon creation.
        """
        out = StringIO()
        call_command('seed_subreddits', number=10, members=4, stdout=out)
        expected_out = ("Creating 10 new subreddits with 4 members each")
        self.assertIn(expected_out, out.getvalue())
        self.assertEqual(Sub.objects.count(), 10)
        self.assertEqual(len(Sub.objects.first().members.all()), 4)
        
    def test_number_of_mods(self):
        """
        For the time being the subreddits created automatically should have
        only a single moderator. And that moderator will be a member
        """
        out = StringIO()
        call_command('seed_subreddits', number=10, members=4, stdout=out)
        for subreddit in Sub.objects.all():
            self.assertEqual(subreddit.moderators.all().count(), 1)
            self.assertIn(
            subreddit.moderators.all().first(),
            subreddit.members.all()
            )
        
                
        
        
