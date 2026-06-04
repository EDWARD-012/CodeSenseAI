"""
API views for CodeSense AI.

Handles HTTP requests for code review, chat, and run-code endpoints.
Each view delegates to the service layer for business logic.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .services.validation_service import validate_review_request, validate_chat_request
from .services.rag_service import retrieve, format_rag_context
from .services.prompt_service import (
    build_review_prompt,
    build_chat_prompt,
    CODE_REVIEW_SYSTEM_PROMPT,
    CHAT_SYSTEM_PROMPT,
)
from .services.ollama_service import generate, chat as ollama_chat, OllamaServiceError

logger = logging.getLogger(__name__)


def _parse_json_body(request) -> tuple[dict | None, JsonResponse | None]:
    """
    Parse JSON body from request.
    Returns (data, None) on success, (None, error_response) on failure.
    """
    try:
        data = json.loads(request.body)
        return data, None
    except (json.JSONDecodeError, ValueError):
        return None, JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body.'
        }, status=400)


def _parse_review_response(raw_text: str) -> dict:
    """
    Attempt to parse the AI's review response as JSON.
    Falls back to raw text if parsing fails.
    """
    # Try to extract JSON from the response (handle markdown fencing)
    text = raw_text.strip()

    # Remove markdown code fencing if present
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    text = text.strip()

    try:
        parsed = json.loads(text)
        return {
            'success': True,
            'summary': parsed.get('summary', ''),
            'issues': parsed.get('issues', []),
            'suggestions': parsed.get('suggestions', []),
            'riskLevel': parsed.get('riskLevel', 'unknown'),
            'positives': parsed.get('positives', []),
        }
    except (json.JSONDecodeError, ValueError):
        logger.warning('Could not parse AI review response as JSON, returning raw text.')
        return {
            'success': True,
            'summary': 'Review completed (unstructured response)',
            'issues': [],
            'suggestions': [],
            'riskLevel': 'unknown',
            'positives': [],
            'rawResponse': raw_text,
        }


def _build_access_token(user) -> tuple[str, int]:
    """Create a signed JWT access token for an authenticated user."""
    now = datetime.now(timezone.utc)
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES)
    expires_at = now + expires_delta
    payload = {
        'sub': str(user.id),
        'username': user.get_username(),
        'iat': int(now.timestamp()),
        'exp': int(expires_at.timestamp()),
        'type': 'access',
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, int(expires_delta.total_seconds())


@csrf_exempt
@require_http_methods(['POST'])
def login(request):
    """
    POST /api/login

    Authenticates via email + password.
    - If email exists → verify password
    - If email is new → auto-register and return token
    - Validates Gmail / any email format

    Request JSON:
        { email, password }

    Response JSON:
        { success, access_token, token_type, expires_in, user, is_new }
    """
    import re
    data, error = _parse_json_body(request)
    if error:
        return error

    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))

    # Validate email format
    email_re = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    if not email or not email_re.match(email):
        return JsonResponse({
            'success': False,
            'error': 'Please enter a valid email address (e.g. you@gmail.com).',
        }, status=400)

    if not password or len(password) < 6:
        return JsonResponse({
            'success': False,
            'error': 'Password must be at least 6 characters.',
        }, status=400)

    User = get_user_model()

    # Derive a username from the email (before the @)
    base_username = email.split('@')[0][:30]

    # Check if user already exists by email
    existing = User.objects.filter(email=email).first()

    if existing:
        # Existing user — verify password
        if not existing.check_password(password):
            return JsonResponse({
                'success': False,
                'error': 'Incorrect password for this email.',
            }, status=401)
        if not existing.is_active:
            return JsonResponse({
                'success': False,
                'error': 'This account has been disabled.',
            }, status=403)
        user = existing
        is_new = False
    else:
        # New user — auto-register
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{suffix}'
            suffix += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        is_new = True

    token, expires_in = _build_access_token(user)
    return JsonResponse({
        'success': True,
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': expires_in,
        'is_new': is_new,
        'user': {
            'id': user.id,
            'username': user.get_username(),
            'email': user.email,
        },
    })


@csrf_exempt
@require_http_methods(['POST'])
def review_code(request):
    """
    POST /api/review-code

    Accepts code for AI review. Validates input, retrieves RAG context,
    builds a prompt, and calls Ollama for analysis.

    Request JSON:
        { code, language, reviewMode }

    Response JSON:
        { success, summary, issues, suggestions, riskLevel, positives }
    """
    # Parse body
    data, error = _parse_json_body(request)
    if error:
        return error

    # Validate
    is_valid, error_msg = validate_review_request(data)
    if not is_valid:
        return JsonResponse({'success': False, 'error': error_msg}, status=400)

    code = data.get('code', '').strip()
    language = data.get('language', 'auto').lower().strip()
    review_mode = data.get('reviewMode', 'general').lower().strip()

    try:
        # Retrieve RAG context
        rag_docs = retrieve(
            code=code,
            language=language,
            review_mode=review_mode,
        )
        rag_context = format_rag_context(rag_docs)

        # Build prompt
        prompt = build_review_prompt(
            code=code,
            language=language,
            review_mode=review_mode,
            rag_context=rag_context,
        )

        # Call Ollama
        raw_response = generate(prompt, system_prompt=CODE_REVIEW_SYSTEM_PROMPT)

        # Parse and return
        result = _parse_review_response(raw_response)
        return JsonResponse(result)

    except OllamaServiceError as e:
        logger.error(f'Ollama service error during review: {e}')
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=503)
    except Exception as e:
        logger.exception(f'Unexpected error during code review: {e}')
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.',
        }, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def chat(request):
    """
    POST /api/chat

    Accepts follow-up questions about code or previous reviews.

    Request JSON:
        { message, code (optional), reviewContext (optional) }

    Response JSON:
        { success, answer }
    """
    data, error = _parse_json_body(request)
    if error:
        return error

    is_valid, error_msg = validate_chat_request(data)
    if not is_valid:
        return JsonResponse({'success': False, 'error': error_msg}, status=400)

    message = data.get('message', '').strip()
    code = data.get('code', '').strip()
    review_context = data.get('reviewContext', '').strip()

    try:
        # Retrieve RAG context for the question
        rag_docs = retrieve(question=message, code=code)
        rag_context = format_rag_context(rag_docs)

        # Build chat messages
        messages = build_chat_prompt(
            message=message,
            code=code,
            review_context=review_context,
            rag_context=rag_context,
        )

        # Call Ollama chat
        answer = ollama_chat(messages, system_prompt=CHAT_SYSTEM_PROMPT)

        return JsonResponse({
            'success': True,
            'answer': answer,
        })

    except OllamaServiceError as e:
        logger.error(f'Ollama service error during chat: {e}')
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=503)
    except Exception as e:
        logger.exception(f'Unexpected error during chat: {e}')
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.',
        }, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def run_code(request):
    """
    POST /api/run-code

    Executes code in a sandboxed subprocess and returns output.

    Request JSON:
        { code, language }

    Response JSON:
        { success, stdout, stderr, exit_code, timed_out, language }
    """
    from .services.execution_service import execute_code

    data, error = _parse_json_body(request)
    if error:
        return error

    code = data.get('code', '').strip()
    language = data.get('language', 'python').lower().strip()
    stdin = data.get('stdin', '')  # Custom stdin for interactive programs

    if not code:
        return JsonResponse({
            'success': False,
            'error': 'No code provided to execute.',
        }, status=400)

    if len(code) > 50000:
        return JsonResponse({
            'success': False,
            'error': 'Code is too large to execute (max 50,000 characters).',
        }, status=400)

    try:
        result = execute_code(code, language, stdin)
        return JsonResponse(result)
    except Exception as e:
        logger.exception(f'Unexpected error during code execution: {e}')
        return JsonResponse({
            'success': False,
            'stdout': '',
            'stderr': f'Server error: {str(e)}',
            'exit_code': -1,
            'timed_out': False,
            'language': language,
        }, status=500)
