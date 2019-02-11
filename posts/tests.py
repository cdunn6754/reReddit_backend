from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError

from redditors.models import User, UserSubMembership
from subs.models import Sub
from posts.models import Post
from votes.models import PostVote

class PostTest(APITestCase):
    """
    General post creation without a request
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
        
        self.post_data = {
            "title": "test post title",
            "body": "Test post body",
        }
        
    def test_post_creation(self):
        """
        Can create a post with a subreddit and a user
        """
        post = Post.objects.create(
            subreddit=self.subreddit,
            poster=self.user,
            **self.post_data
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertIs(post.poster, self.user)
        self.assertIs(post.subreddit, self.subreddit)
        self.assertEqual(post.title, self.post_data["title"])
        self.assertEqual(post.body, self.post_data["body"])
        
    def test_post_creation_long_title(self):
        """
        The maximum title length is 150 chars
        """
        error_message = "The title can only be 150 characters in length."
        with self.assertRaises(ValidationError):
            post = Post(
                subreddit=self.subreddit,
                poster=self.user,
                title = 'a'*151,
                body = "test body"
            )
            post.full_clean()
        
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
        
        
class PostRetrieveRequestTests(APITestCase):
    """
    Testing request for retrieving lists of posts, including
    pseudo-subreddits and pagination
    """
    def setUp(self):
        # need a subreddit
        self.subreddit = Sub.objects.create(
            title='test_subreddit'
        )

        # and a user or two
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
        
        for post_num in range(10):
            Post.objects.create(
                poster=self.user,
                subreddit=self.subreddit,
                title="user_1_post_title_{}".format(post_num)
            )
        for post_num in range(10):
            Post.objects.create(
                poster=self.user2,
                subreddit=self.subreddit,
                title="user_2_post_title_{}".format(post_num)
            )
        
        self.sub_post_list_url = reverse(
            'sub-post-list',
            kwargs={ "sub_title": self.subreddit.title}
        )
        self.sub_post_list_url_f = lambda title: reverse(
            'sub-post-list',
            kwargs={ "sub_title": title}
        )

    def test_real_subreddit_retrieval(self):
        """
        An unauthed user can retrive all of the posts from a particular
        subreddit.
        """
        response = self.client.get(self.sub_post_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "user_1_post_title_", count=10)
        self.assertContains(response, "user_2_post_title_", count=10)
        
    def test_real_non_subreddit_retrieval(self):
        """
        A request for the posts of a subreddit that doesn't exist
        raises a 404
        """
        response = self.client.get(self.sub_post_list_url_f("non_sub"))
        self.assertContains(
            response,
            "The 'non_sub' subreddit does not exist",
            count=1,
            status_code=404
        )
        
    def test_pseudo_home_subreddit_retrieval(self):
        """
        An unauthed request to the 'Home' psuedo subReddit returns
        a list of all of the posts
        """
        response = self.client.get(self.sub_post_list_url_f("Home"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "user_1_post_title_", count=10)
        self.assertContains(response, "user_2_post_title_", count=10)
        
    def test_auth_pseudo_home_subreddit_retrieval(self):
        """
        An authenticated request to the 'Home' psuedo subReddit returns
        a list of all of the posts for the subreddits the user is subcribed to
        """
        self.client.force_login(self.user)
        # create a new subreddit for this test
        self.subreddit2 = Sub.objects.create(
            title='test_subreddit_2'
        )
        # sign up for the subreddit
        UserSubMembership.objects.create(
            user=self.user,
            sub=self.subreddit2
        )
        # make some posts in new subreddit
        for post_num in range(10):
            Post.objects.create(
                poster=self.user,
                subreddit=self.subreddit2,
                title="these_are_in_sub2_{}".format(post_num)
            )
        response = self.client.get(self.sub_post_list_url_f("Home"))
        self.assertContains(
            response,
            "these_are_in_sub2_",
            count=10
        )
        self.assertNotContains(response, "user_1_post_title_")
        self.assertNotContains(response, "user_2_post_title_")
        
    def test_pseudo_popular_subreddit_retrieval(self):
        """
        Should only return the popular posts, at this point that
        means posts with more than on upvote.
        """
        # pick half of the 20 posts we made in setUp to become popular
        evens = range(0,10,2)
        for post in Post.objects.all():
            if int(post.title[-1]) in evens:
                PostVote.objects.create(
                    post=post,
                    user=self.user,
                    vote_type=1
                )
                PostVote.objects.create(
                    post=post,
                    user=self.user2,
                    vote_type=1
                )
        
        response = self.client.get(self.sub_post_list_url_f("Popular"))
        self.assertContains(response, "user_1_post_title_", count=5)
        self.assertContains(response, "user_2_post_title_", count=5)
        self.assertNotContains(response, "user_1_post_title_1")
        self.assertNotContains(response, "user_2_post_title_3")
        
    def test_pseudo_all_subreddit_retrieval(self):
        """
        Should only return the all posts, at this point that
        means posts with more than on upvote.
        NOTE: at this point the all subreddit is identical to the
        popular subreddit so this test is also identical
        """
        # pick half of the 20 posts we made in setUp to become popular
        evens = range(1,11,2)
        for post in Post.objects.all():
            if int(post.title[-1]) in evens:
                PostVote.objects.create(
                    post=post,
                    user=self.user,
                    vote_type=1
                )
                PostVote.objects.create(
                    post=post,
                    user=self.user2,
                    vote_type=1
                )
        
        response = self.client.get(self.sub_post_list_url_f("All"))
        self.assertContains(response, "user_1_post_title_", count=5)
        self.assertContains(response, "user_2_post_title_", count=5)
        self.assertNotContains(response, "user_1_post_title_0")
        self.assertNotContains(response, "user_2_post_title_2")
        
    def test_pagination(self):
        """
        requests can specify limit and offset GET query parameters to
        indicate pagination requirements
        """
        # make some more posts
        for post_num in range(10):
            Post.objects.create(
                poster=self.user,
                subreddit=self.subreddit,
                title="pagination_user_1_post_title_{}".format(post_num)
            )

        pagination_parameters = {
            'offset': 0,
            'limit': 5
        }
        response = self.client.get(self.sub_post_list_url, pagination_parameters)
        self.assertContains(response, "user_1_post_title_", count=5)
        self.assertNotContains(response, "user_2_post_title_")
        
        pagination_parameters = {
            'offset': 5,
            'limit': 10
        }
        response = self.client.get(self.sub_post_list_url, pagination_parameters)
        self.assertContains(response, "user_1_post_title_", count=5)
        self.assertContains(response, "user_2_post_title_", count=5)
        
        pagination_parameters = {
            'offset': 15,
            'limit': 5
        }
        response = self.client.get(self.sub_post_list_url, pagination_parameters)
        self.assertContains(response, "user_2_post_title_", count=5)
        self.assertNotContains(response, "user_1_post_title_")

    def test_pagination_next(self):
        """
        The pagination response contains a 'next' hyperlink that can
        be followed to retrieve the next set.
        """
        pagination_parameters = {
            'offset': 0,
            'limit': 10
        }
        response = self.client.get(self.sub_post_list_url, pagination_parameters)
        response = self.client.get(response.data["next"])
        self.assertContains(response, "user_2_post_title_", count=10)
        self.assertNotContains(response, "user_1_post_title_")
        
    def test_pagination_next_with_orderby(self):
        """
        The orderby query parameter should be preserved to the
        'next' hyperlink of the pagination response. And the ordering
        should still work.
        """
        # make half of the posts popular
        evens = range(1,11,2)
        for post in Post.objects.all():
            if int(post.title[-1]) in evens:
                PostVote.objects.create(
                    post=post,
                    user=self.user,
                    vote_type=1
                )
                PostVote.objects.create(
                    post=post,
                    user=self.user2,
                    vote_type=1
                )
                        
        pagination_parameters = {
            'offset': 0,
            'limit': 10
        }
        q_params = {
            **pagination_parameters,
            "orderby": "popular"
        }
        response = self.client.get(self.sub_post_list_url_f("Home"), q_params)
        self.assertContains(response, "user_1_post_title_", count=5)
        self.assertContains(response, "user_2_post_title_", count=5)
        self.assertIn("orderby=popular", response.data["next"])
        # make sure they were all the popular ones
        popularity = []
        for post in response.data["results"]:
            popularity.append(post["upvotes"]==2)
        self.assertTrue(all(popularity))
        
        # now make sure these are the unpopular ones
        response = self.client.get(response.data["next"])
        popularity = []
        for post in response.data["results"]:
            popularity.append(post["upvotes"]==0)
        self.assertTrue(all(popularity))
        
        
