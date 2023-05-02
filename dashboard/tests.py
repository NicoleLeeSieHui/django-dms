from django.test import TestCase, Client
from .models import File_upload
from django.urls import reverse
import time

class TestResponseTime(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_response_time(self):
        url = reverse('homepage')
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        response_time = end_time - start_time
        self.assertLess(response_time, 1, 'Response time should be less than 1 second')

class TestResponseTime2(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_response_time(self):
        url = reverse('register')
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        response_time = end_time - start_time
        self.assertLess(response_time, 1, 'Response time should be less than 1 second')


class MyModelTestCase(TestCase):
    def setUp(self):
        self.my_model = File_upload.objects.create(title='Test')

    def test_my_model(self):
        self.assertEqual(self.my_model.title, 'Test')


