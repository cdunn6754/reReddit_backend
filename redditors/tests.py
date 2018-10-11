from django.test import TestCase
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status

from .models import User

# Create your tests here.

class UserTestCase(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create('tester', 'test@gmail.com',
                                             'testpassword')
        
