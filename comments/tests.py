from django.test import TestCase
from django.db import transaction
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.core.management import call_command
from io import StringIO

from comments.models import Comment
from posts.models import Post
from redditors.models import User
from subs.models import Sub

class CommentTest(APITestCase):
    """
    Basic database creation and destruction without any request/view testing
    """
    def setUp(self):
        # need to set up quite a bit of background
        self.user = User.objects.create(
            username="test_user1",
            email="test1@gmail.com",
            password="testpassword"
        )
        self.subreddit = Sub.objects.create(
            title="test_subreddit",
        )
        self.post = Post.objects.create(
            title="test_post_title",
            body="test_post_body",
            subreddit=self.subreddit,
            poster=self.user
        )
        
    def create_comment(self, **kwargs):
        return Comment.objects.create(
            poster=kwargs.get("poster"),
            post=kwargs.get("post"),
            parent=kwargs.get("parent")
        )
        
    def test_root_comment_creation(self):
        """
        Create a root comment should add one to the db with the proper fields
        """
        comment = self.create_comment(
            poster=self.user,
            post=self.post
        )
        self.assertEqual(comment.poster, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertIsNone(comment.parent)
        self.assertEqual(len(comment.children.all()), 0)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertIsInstance(comment, Comment)
        self.assertFalse(comment.deleted)
        
    def test_child_comment_creation(self):
        """
        Create a child comment should add one to the db with the proper fields
        """
        # need a root first
        root_comment = self.create_comment(
            poster=self.user,
            post=self.post
        )
        
        comment = self.create_comment(
            poster=self.user,
            parent=root_comment
        )
        self.assertEqual(comment.parent, root_comment)
        self.assertEqual(comment.poster, self.user)
        self.assertIsNone(comment.post)
        self.assertEqual(len(comment.children.all()), 0)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertIsInstance(comment, Comment)
        self.assertFalse(comment.deleted)
        
        self.assertEqual(len(root_comment.children.all()), 1)
        self.assertIn(comment, root_comment.children.all())
        
class CommentViewTests(APITestCase):
    """
    Testing the various requests on comments
    """
    def setUp(self):
        # need to set up quite a bit of background
        self.user = User.objects.create(
            username="test_user1",
            email="test1@gmail.com",
            password="testpassword"
        )
        self.subreddit = Sub.objects.create(
            title="test_subreddit",
        )
        self.post = Post.objects.create(
            title="test_post_title",
            body="test_post_body",
            subreddit=self.subreddit,
            poster=self.user
        )
        
        self.comment_body = "comment test body"
        
        self.comment_list_url = reverse('comment-list')
        self.comment_detail_url =  lambda pk: reverse(
            'comment-detail',
            kwargs={"pk": pk}
        )
        
        self.client.force_login(self.user)
        
    def create_comment(self, **kwargs):
        return Comment.objects.create(
            poster=kwargs.get("poster"),
            post=kwargs.get("post"),
            parent=kwargs.get("parent")
        )

    def test_root_comment_creation(self):
        """
        A root comment is created with a post fullname as the parent.
        Then in the response the parent (i.e. parent comment)
        should be None and the post should be set.
        """
        
        parent_fn = "t2_{}".format(self.post.pk)
        data = {
            "parent_fn": parent_fn,
            "body": self.comment_body
        }
        response = self.client.post(self.comment_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data["post"], self.post.title)
        self.assertIsNone(response.data["parent"])
        self.assertEqual(response.data["body"], self.comment_body)
        self.assertFalse(response.data["deleted"])

    def test_child_comment_creation(self):
        """
        A child comment can be created through the list view with a
        comment fullname parameter
        """
        # first create the parent comment via client
        data = {
            "parent_fn": "t2_{}".format(self.post.pk),
            "body": "root comment body"
        }
        root_response = self.client.post(self.comment_list_url, data)
        root_comment = Comment.objects.get(
            pk=int(root_response.data["pk"])
        )
        
        data = {
            "parent_fn": "t1_{}".format(root_comment.pk),
            "body": self.comment_body
        }
        response = self.client.post(self.comment_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(response.data["body"], self.comment_body)
        self.assertEqual(response.data["parent"], root_comment.pk)
        self.assertIsNone(response.data["post"])
        self.assertFalse(response.data["deleted"])
        
        self.assertIn(
            Comment.objects.get(pk=int(response.data["pk"])),
            root_comment.children.all()
        )
        
    def test_root_comment_deletion(self):
        """
        When deleted through a request the comment is not actually
        removed from the db, instead certain fields are set to None.
        That way the comment can still be shown in hierarchichal trees.
        """
        
        parent_fn = "t2_{}".format(self.post.pk)
        data = {
            "parent_fn": parent_fn,
            "body": self.comment_body
        }
        response = self.client.post(self.comment_list_url, data)
        comment = Comment.objects.get(
            pk=int(response.data["pk"])
        )
        response = self.client.delete(self.comment_detail_url(comment.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertTrue(response.data["deleted"])
        self.assertIsNone(response.data["poster"])
        self.assertIs(response.data["body"], "deleted")
        self.assertEqual(response.data["post"], self.post.title)

    def test_child_comment_deletion(self):
        """
        When a child comment is deleted it remains in the database
        and the link to and from the parent comment remains
        """
        # first create the parent comment via client
        data = {
            "parent_fn": "t2_{}".format(self.post.pk),
            "body": "root comment body"
        }
        root_response = self.client.post(self.comment_list_url, data)
        root_comment = Comment.objects.get(
            pk=int(root_response.data["pk"])
        )
        # Create a child comment
        data = {
            "parent_fn": "t1_{}".format(root_comment.pk),
            "body": self.comment_body
        }
        response = self.client.post(self.comment_list_url, data)
        comment = Comment.objects.get(
            pk=int(response.data["pk"])
        )
        # Create a grandchild comment
        data = {
            "parent_fn": "t1_{}".format(comment.pk),
            "body": self.comment_body
        }
        gc_response = self.client.post(self.comment_list_url, data)
        gc_comment = Comment.objects.get(
            pk=int(gc_response.data["pk"])
        )
        # delete the child comment
        response = self.client.delete(self.comment_detail_url(comment.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            root_comment.children.first().children.first(),
            gc_comment
        )
        self.assertTrue(response.data["deleted"])
        self.assertFalse(gc_comment.deleted)
        self.assertFalse(root_comment.deleted)
