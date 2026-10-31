from django.test import TestCase
from django.urls import reverse
from django.contrib.staticfiles import finders


class HomeTests(TestCase):
    def test_home_serves_prototype(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ondjango')
        self.assertContains(response, '/static/learning/main.js')

    def test_assets_exist(self):
        self.assertIsNotNone(finders.find('learning/main.js'))
        self.assertIsNotNone(finders.find('learning/style.css'))
