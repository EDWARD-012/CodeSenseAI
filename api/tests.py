"""
Basic API tests for CodeSense AI.
Tests validation, endpoint structure, and error handling.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch
from django.core import signing
import json


class _MockLLMResponse:
    text = '{"ok": true}'

    def raise_for_status(self):
        return None

    def json(self):
        return {'choices': [{'message': {'content': 'Fast answer'}}]}


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
            data=json.dumps({'email': 'alice@example.com', 'password': 'correct-password'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['token_type'], 'Bearer')
        self.assertEqual(data['expires_in'], 604800)
        self.assertEqual(data['user']['username'], 'alice')

        payload = signing.loads(data['access_token'], salt='codesense-auth-token')
        self.assertEqual(payload['sub'], str(self.user.id))
        self.assertEqual(payload['username'], 'alice')
        self.assertEqual(payload['email'], 'alice@example.com')

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'email': 'alice@example.com', 'password': 'wrong-password'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()['success'])

    def test_login_requires_username_and_password(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'email': 'alice@example.com'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_login_rejects_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.url,
            data=json.dumps({'email': 'alice@example.com', 'password': 'correct-password'}),
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

    @patch('api.views.ollama_chat')
    def test_chat_returns_ai_answer(self, mock_chat):
        mock_chat.return_value = 'Use a guard clause before indexing the list.'

        response = self.client.post(
            self.url,
            data=json.dumps({
                'message': 'How do I fix this?',
                'code': 'items = []\nprint(items[0])',
                'reviewContext': 'IndexError risk',
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('guard clause', data['answer'])
        mock_chat.assert_called_once()


class LLMServiceTests(TestCase):
    """Tests for the NVIDIA/OpenAI-compatible LLM service wrapper."""

    @patch.dict('os.environ', {'NVIDIA_API_KEY': 'test-key', 'LLM_CHAT_MODEL': 'fast-chat-model'})
    @patch('api.services.ollama_service.requests.post')
    def test_chat_uses_configured_chat_model(self, mock_post):
        from api.services.ollama_service import chat

        mock_post.return_value = _MockLLMResponse()

        answer = chat([{'role': 'user', 'content': 'Hi'}], system_prompt='Be concise')

        self.assertEqual(answer, 'Fast answer')
        payload = mock_post.call_args.kwargs['json']
        self.assertEqual(payload['model'], 'fast-chat-model')
        self.assertEqual(payload['max_tokens'], 700)


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
        mock_execute_code.assert_called_once_with('print("hi")', 'python', '')


class HomePageTests(TestCase):
    """Tests for the home page."""

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CodeSense AI')
