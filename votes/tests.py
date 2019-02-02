from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from redditors.models import User, UserSubMembership
from subs.models import Sub
from posts.models import Post
from comments.models import Comment
from votes.models import CommentVote, PostVote

class VoteTestBase(APITestCase):
    """
    There is a lot of setup necessary for testing votes.
    This class will help get some of that out of the way
    """
    def setUp(self):
        self.subreddit = Sub.objects.create(
            title='test_subreddit'
        )
        
        # two users  are needed, one creates content, 'poster' the other
        # votes on it 'voter'
        self.poster_data = {
            'username': 'test_username',
            'email': 'test@gmail.com',
            'password': 'test_password',
            }
        self.poster = User.objects.create(**self.poster_data)
        self.voter_data = {
            'username': 'test_username_2',
            'email': 'test2@gmail.com',
            'password': 'test_password',
            }
        self.voter = User.objects.create(**self.voter_data)
        
        self.post = Post.objects.create(
            title="test_post_title",
            body="test_post_body",
            subreddit=self.subreddit,
            poster=self.poster
        )
        self.comment = Comment.objects.create(
            body="test comment",
            post=self.post,
            parent=None,
            poster=self.poster
        )
        self.client.force_login(self.voter)
        
        self.vote_url = reverse('vote')
        
        self.comment_vote_data =  lambda vote_type : {
            "item_fn": "t1_{}".format(self.comment.pk),
            "vote_type": vote_type
        }
        self.post_vote_data =  lambda vote_type : {
            "item_fn": "t2_{}".format(self.post.pk),
            "vote_type": vote_type
        }
        self.vote_data = lambda type, vote_type : {
            "item_fn": "{}_{}".format(type, self.post.pk),
            "vote_type": vote_type
        }
        
        self.class_type = {
            "t1": CommentVote,
            "t2": PostVote
        }

class VoteViewTests(VoteTestBase):
    """
    Testing vote creation and updating with requests
    """
    def test_upvote(self):
        """
        An authorized user can upvote on a comment and a post
        """
        for key in self.class_type.keys():
            response = self.client.post(self.vote_url, self.vote_data(key, 1))
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(self.class_type[key].objects.count(), 1)
            self.assertEqual(self.class_type[key].objects.first().vote_type, 1)
            
    def test_downvote(self):
        """
        An authorized user can downvote on a comment and a post
        """
        for key in self.class_type.keys():
            response = self.client.post(self.vote_url, self.vote_data(key, -1))
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(self.class_type[key].objects.count(), 1)
            self.assertEqual(self.class_type[key].objects.first().vote_type, -1)
    
    def test_double_vote(self):
        """
        A double vote updates the original vote to a non-vote
        it does not add another vote instance to the database.
        """
        vote_types = [1, -1]
        for vote_type in vote_types:
            for (key, class_name) in self.class_type.items():
                response = self.client.post(
                    self.vote_url,
                    self.vote_data(key, vote_type)
                )
                response = self.client.post(
                    self.vote_url,
                    self.vote_data(key, vote_type)
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(class_name.objects.count(), 1)
                self.assertEqual(
                    class_name.objects.first().vote_type,
                    0
                )
        # there is also a direct unvote option
        for key in self.class_type.keys():
            response = self.client.post(self.vote_url, self.vote_data(key, 1))
            response = self.client.post(self.vote_url, self.vote_data(key, 0))
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(self.class_type[key].objects.count(), 1)
            self.assertEqual(self.class_type[key].objects.first().vote_type, 0)
            

    def test_unauthed_vote(self):
        """
        An unauthed user can not vote
        """
        self.client.logout()
        for (key, class_name) in self.class_type.items():
            response = self.client.post(self.vote_url, self.vote_data(key, 1))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(class_name.objects.count(), 0)

class VoteKarmaAddition(VoteTestBase):
    """
    Post and comment Vote requests and their effect on the posters's
    karma
    """
        
    def test_comment_vote(self):
        """
        When a comment is voted on the poster's karma should change
        appropriately
        """
        # make an upvote
        original_karma = self.poster.karma
        response = self.client.post(self.vote_url, self.comment_vote_data(1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommentVote.objects.first().vote_type, 1)
        self.assertEqual(self.poster.karma, original_karma + 1)
        
        # upvote again, that cancels original vote
        response = self.client.post(self.vote_url, self.comment_vote_data(1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommentVote.objects.first().vote_type, 0)
        self.assertEqual(self.poster.karma, original_karma)
        
        # make a downvote
        response = self.client.post(self.vote_url, self.comment_vote_data(-1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommentVote.objects.first().vote_type, -1)
        self.assertEqual(self.poster.karma, original_karma - 1)
        
        # from downvote to upvote
        response = self.client.post(self.vote_url, self.comment_vote_data(1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommentVote.objects.first().vote_type, 1)
        self.assertEqual(self.poster.karma, original_karma + 1)
        
        # test an unvote
        response = self.client.post(self.vote_url, self.comment_vote_data(0))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommentVote.objects.first().vote_type, 0)
        self.assertEqual(self.poster.karma, original_karma)
        
        # no change in karma on unauthed vote
        self.client.logout()
        response = self.client.post(self.vote_url, self.comment_vote_data(1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CommentVote.objects.first().vote_type, 0)
        self.assertEqual(self.poster.karma, original_karma)
        
    def test_post_vote(self):
        """
        When a post is voted on the poster's karma should change
        appropriately
        """
        # make an upvote
        original_karma = self.poster.karma
        response = self.client.post(self.vote_url, self.post_vote_data(1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PostVote.objects.first().vote_type, 1)
        self.assertEqual(self.poster.karma, original_karma + 1)
        
        # upvote again, that cancels original vote
        response = self.client.post(self.vote_url, self.post_vote_data(1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PostVote.objects.first().vote_type, 0)
        self.assertEqual(self.poster.karma, original_karma)
        
        # make a downvote
        response = self.client.post(self.vote_url, self.post_vote_data(-1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PostVote.objects.first().vote_type, -1)
        self.assertEqual(self.poster.karma, original_karma - 1)
        
        # from downvote to upvote
        response = self.client.post(self.vote_url, self.post_vote_data(1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PostVote.objects.first().vote_type, 1)
        self.assertEqual(self.poster.karma, original_karma + 1)
        
        # test an unvote
        response = self.client.post(self.vote_url, self.post_vote_data(0))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PostVote.objects.first().vote_type, 0)
        self.assertEqual(self.poster.karma, original_karma)
        
        # no change in karma on unauthed vote
        self.client.logout()
        response = self.client.post(self.vote_url, self.comment_vote_data(1))
        self.poster.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PostVote.objects.first().vote_type, 0)
        self.assertEqual(self.poster.karma, original_karma)
        
        
        
