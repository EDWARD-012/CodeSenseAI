"""
Basic API tests for CodeSense AI.
Tests validation, endpoint structure, and error handling.
"""

from django.test import TestCase, Client
import json


class ReviewCodeTests(TestCase):
    """Tests for the /api/review-code endpoint."""

    def setUp(self):
        self.client = Client()
        self.url = '/api/review-code'

    def test_empty_code_returns_400(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'code': '', 'language': 'python', 'reviewMode': 'general'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])

    def test_missing_body_returns_400(self):
        response = self.client.post(
            self.url,
            data='not json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_oversized_code_returns_400(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'code': 'x' * 30000, 'language': 'python', 'reviewMode': 'general'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_unsupported_language(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'code': 'print("hi")', 'language': 'brainfuck', 'reviewMode': 'general'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class ChatTests(TestCase):
    """Tests for the /api/chat endpoint."""

    def setUp(self):
        self.client = Client()
        self.url = '/api/chat'

    def test_empty_message_returns_400(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class RunCodeTests(TestCase):
    """Tests for the /api/run-code endpoint."""

    def setUp(self):
        self.client = Client()
        self.url = '/api/run-code'

    def test_returns_501(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'code': 'print("hi")'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 501)
        data = response.json()
        self.assertFalse(data['success'])


class HomePageTests(TestCase):
    """Tests for the home page."""

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CodeSense AI')
