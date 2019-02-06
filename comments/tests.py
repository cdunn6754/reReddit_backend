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
        self.assertEqual(response.data["post"]["pk"], self.post.pk)
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
        self.assertContains(response, self.post.title, status_code=201)
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
        self.assertEqual(response.data["body"], "deleted")
        self.assertEqual(response.data["post"]["pk"], self.post.pk)

    def test_child_comment_deletion(self):
        """
        When a child comment is deleted it remains in the database
        and the link to and from the parent comment remains
        """
        # first create the parent comment via client
        rc_body = "root comment body"
        data = {
            "parent_fn": "t2_{}".format(self.post.pk),
            "body": rc_body
        }
        root_response = self.client.post(self.comment_list_url, data)
        self.assertContains(root_response, rc_body, status_code=201)
        self.assertEqual(Comment.objects.count(), 1)
        root_comment = Comment.objects.get(
            pk=int(root_response.data["pk"])
        )
        # Create a child comment
        data = {
            "parent_fn": "t1_{}".format(root_comment.pk),
            "body": self.comment_body
        }
        response = self.client.post(self.comment_list_url, data)
        self.assertContains(response, self.comment_body, status_code=201)
        self.assertEqual(Comment.objects.count(), 2)
        comment = Comment.objects.get(
            pk=int(response.data["pk"])
        )
        # Create a grandchild comment
        gc_body = "grandchild body"
        data = {
            "parent_fn": "t1_{}".format(comment.pk),
            "body": gc_body
        }
        gc_response = self.client.post(self.comment_list_url, data)
        self.assertContains(gc_response, gc_body, status_code=201)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(
            gc_response.data["post"],
            response.data["post"]
        )
        self.assertEqual(
            gc_response.data["post"],
            root_response.data["post"]
        )
        self.assertEqual(
            gc_response.data["post"]["pk"],
            self.post.pk
        )
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
        
        
class SeedCommentsSubredditCommandTests(TestCase):
    def setUp(self):
        # need to get users, subreddits and posts first
        out = StringIO()
        call_command('seed_users', number=5, stdout=out)
        call_command('seed_subreddits', number=5, stdout=out)
        call_command('seed_posts', number=10, stdout=out)
    
    def test_seed_root_comments(self):
        """
        Can create a user specified number of root comments
        """
        out = StringIO()
        call_command('seed_comments', number_roots=10, stdout=out)
        expected_out = "Creating 10 new root comments"
        self.assertIn(expected_out, out.getvalue())
        self.assertEqual(Comment.objects.count(), 10)

    def test_seed_child_comments(self):
        """
        Can create a user specified number of child comments
        """
        out1 = StringIO()
        call_command('seed_comments', number_roots=5, stdout=out1)
        out = StringIO()
        call_command('seed_comments', number_children=10, stdout=out)
        expected_out = "Creating 10 new child comments"
        self.assertIn(expected_out, out.getvalue())
        self.assertEqual(Comment.objects.count(), 15)
        for comment in Comment.objects.all():
            self.assertIsNotNone(comment.post)
