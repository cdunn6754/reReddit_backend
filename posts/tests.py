from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from redditors.models import User, UserSubMembership
from subs.models import Sub
from posts.models import Post

class PostRequestTests(APITestCase):
    """
    Testing request for making, updating and deleting posts
    """
    def setUp(self):
        # need a subreddit
        self.subreddit = Sub.objects.create(
            title='test_subreddit'
        )

        # and a user
        self.user_data = {
            'username': 'test_username',
            'email': 'test@gmail.com',
            'password': 'test_password',
            }
        self.user = User.objects.create(**self.user_data)
        self.user_data_2 = {
            'username': 'test_username_2',
            'email': 'test2@gmail.com',
            'password': 'test_password',
            }
        self.user2 = User.objects.create(**self.user_data_2)
        

        self.client.force_login(self.user)
        
        self.create_post_url_f = lambda title: reverse(
            'create-post',
            kwargs={ "sub_title": title}
        )
        self.create_post_url = reverse(
            'create-post',
            kwargs={ "sub_title": self.subreddit.title}
        )
        self.detail_post_url = lambda pk: reverse(
            'post-detail',
            kwargs={ "pk": pk}
        )
        self.post_data = {
            "title": "test post title",
            "body": "Test post body",
        }
        
    def test_create_post_non_member(self):
        """
        Can't create a post to a subreddit without a subreddit membership
        """
        response = self.client.post(self.create_post_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(self.subreddit.posts.count(), 0)
        self.assertEqual(self.user.posts.count(), 0)
        self.assertContains(
            response,
            "You must be a member of the subreddit to post here.",
            status_code=400
        )
        
    def test_create_post_member(self):
        """
        A member of a subreddit can create a post there
        """
        UserSubMembership.objects.create(
            user=self.user,
            sub=self.subreddit
        )
        response = self.client.post(self.create_post_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(self.subreddit.posts.count(), 1)
        self.assertEqual(self.user.posts.count(), 1)
        self.assertNotIn(response.data["pk"], self.user.posts.all())
        self.assertNotIn(response.data["pk"], self.subreddit.posts.all())
        self.assertEqual(response.data["subreddit"], self.subreddit.pk)
        self.assertEqual(response.data["subreddit_title"], self.subreddit.title)
        self.assertEqual(response.data["poster"], self.user.pk)
        self.assertEqual(response.data["poster_username"], self.user.username)
        
    def test_post_creation_psuedo_subreddit(self):
        """
        Should not be able to post to All, Popular, or Home subreddits
        """
        pseudo_names = ["Home", "home", "hOme", "Popular", "All"]
        for title in pseudo_names:
            response = self.client.post(
                self.create_post_url_f(title),
                self.post_data
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Post.objects.count(), 0)
        
    def test_post_update_poster(self):
        """
        The creator of a post can update it
        """
        UserSubMembership.objects.create(
            user=self.user,
            sub=self.subreddit
        )
        post = Post.objects.create(
            subreddit=self.subreddit,
            poster=self.user,
            **self.post_data
        )
        
        self.assertEqual(Post.objects.count(), 1)
        update_data = {
         "body": "new body"
        }
        response = self.client.patch(self.detail_post_url(post.pk), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.data["body"], update_data["body"])
        
    def test_post_update_non_poster(self):
        """
        The if you didn't create the post you can't update
        unless your a moderator
        """
        UserSubMembership.objects.create(
            user=self.user2,
            sub=self.subreddit
        )
        post = Post.objects.create(
            subreddit=self.subreddit,
            poster=self.user2,
            **self.post_data
        )
        update_data = {
         "body": "new body"
        }
        response = self.client.patch(self.detail_post_url(post.pk), update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # make user a moderator
        self.subreddit.moderators.add(self.user)
        response = self.client.patch(self.detail_post_url(post.pk), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.data["body"], update_data["body"])
        
        
    def test_post_delete_poster(self):
        """
        The creator of a post can delete it
        """
        UserSubMembership.objects.create(
            user=self.user,
            sub=self.subreddit
        )
        post = Post.objects.create(
            subreddit=self.subreddit,
            poster=self.user,
            **self.post_data
        )
        
        self.assertEqual(Post.objects.count(), 1)
        response = self.client.delete(self.detail_post_url(post.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)
        
    def test_post_delete_non_poster(self):
        """
        A user who did not create the post can't delete it
        unless they are a moderator of the subreddit
        """
        UserSubMembership.objects.create(
            user=self.user2,
            sub=self.subreddit
        )
        post = Post.objects.create(
            subreddit=self.subreddit,
            poster=self.user2,
            **self.post_data
        )
        
        self.assertEqual(Post.objects.count(), 1)
        response = self.client.delete(self.detail_post_url(post.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)
        
        # make user a moderator
        self.subreddit.moderators.add(self.user)
        response = self.client.delete(self.detail_post_url(post.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)
        
        
