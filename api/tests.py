"""
Basic API tests for CodeSense AI.
Tests validation, endpoint structure, and error handling.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.conf import settings
from unittest.mock import patch
import json
import jwt


class LoginTests(TestCase):
    """Tests for the /api/login endpoint."""

    def setUp(self):
        self.client = Client()
        self.url = '/api/login'
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='correct-password',
        )

    def test_login_returns_jwt_for_valid_credentials(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                'username': 'alice',
                'password': 'correct-password',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['token_type'], 'Bearer')
        self.assertEqual(data['expires_in'], 3600)
        self.assertEqual(data['user']['username'], 'alice')

        payload = jwt.decode(
            data['access_token'],
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        self.assertEqual(payload['sub'], str(self.user.id))
        self.assertEqual(payload['username'], 'alice')
        self.assertEqual(payload['type'], 'access')

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                'username': 'alice',
                'password': 'wrong-password',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()['success'])

    def test_login_requires_username_and_password(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'username': 'alice'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_login_rejects_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.url,
            data=json.dumps({
                'username': 'alice',
                'password': 'correct-password',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()['success'])


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

    @patch('api.services.execution_service.execute_code')
    def test_returns_execution_result(self, mock_execute_code):
        mock_execute_code.return_value = {
            'success': True,
            'stdout': 'hi\n',
            'stderr': '',
            'exit_code': 0,
            'timed_out': False,
            'language': 'python',
        }

        response = self.client.post(
            self.url,
            data=json.dumps({'code': 'print("hi")', 'language': 'python'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['stdout'], 'hi\n')
        mock_execute_code.assert_called_once_with('print("hi")', 'python')


class HomePageTests(TestCase):
    """Tests for the home page."""

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CodeSense AI')
