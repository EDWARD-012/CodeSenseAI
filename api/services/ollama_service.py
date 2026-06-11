"""
LLM service for CodeSense AI — NVIDIA NIM API.

Uses NVIDIA NIM (OpenAI-compatible) endpoint.
Set NVIDIA_API_KEY in Vercel environment variables.
"""

import logging
import os
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OllamaServiceError(Exception):
    """Raised when LLM API communication fails."""
    pass


def _get_api_key() -> str:
    key = (
        getattr(settings, 'NVIDIA_API_KEY', None)
        or os.environ.get('NVIDIA_API_KEY', '')
    )
    if not key or key.strip() in ('', 'put_your_key_here'):
        raise OllamaServiceError(
            'AI service is not configured. '
            'Please set the NVIDIA_API_KEY environment variable in your Vercel project settings.'
        )
    return key.strip()


def _post_nim(messages: list[dict], model: str, max_tokens: int, temperature: float, timeout: int) -> str:
    """Make a single POST request to NVIDIA NIM and return the text content."""
    api_key = _get_api_key()
    url = 'https://integrate.api.nvidia.com/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    payload = {
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'stream': False,
    }

    try:
        logger.info(f'NIM API call: model={model}, messages={len(messages)}')
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content']
        if not content:
            raise OllamaServiceError('AI returned an empty response.')
        return content

    except requests.exceptions.Timeout:
        logger.error(f'NVIDIA NIM timed out after {timeout}s')
        raise OllamaServiceError('AI response timed out. Please try again.')

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        body   = e.response.text[:300]
        logger.error(f'NVIDIA NIM HTTP {status}: {body}')
        if status == 401:
            raise OllamaServiceError(
                'Invalid NVIDIA API key. Please check the NVIDIA_API_KEY in Vercel settings.'
            )
        if status == 429:
            raise OllamaServiceError('AI rate limit reached. Please wait a moment and try again.')
        raise OllamaServiceError(f'AI server error ({status}). Please try again.')

    except OllamaServiceError:
        raise
    except Exception as e:
        logger.exception(f'Unexpected NIM error: {e}')
        raise OllamaServiceError('Failed to connect to AI service. Please try again.')


def generate(prompt: str, system_prompt: str = '') -> str:
    """Single-turn text generation (used for code review)."""
    model   = os.environ.get('LLM_MODEL', 'meta/llama-3.1-70b-instruct')
    timeout = int(getattr(settings, 'REQUEST_TIMEOUT_SECONDS', 90))
    max_tok = int(getattr(settings, 'REVIEW_MAX_TOKENS', 1800))

    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})

    return _post_nim(messages, model, max_tok, 0.2, timeout)


def chat(messages: list[dict], system_prompt: str = '') -> str:
    """Multi-turn chat (used for AI assistant)."""
    model   = os.environ.get('LLM_CHAT_MODEL', os.environ.get('LLM_MODEL', 'meta/llama-3.1-70b-instruct'))
    timeout = int(getattr(settings, 'CHAT_REQUEST_TIMEOUT_SECONDS',
                          getattr(settings, 'REQUEST_TIMEOUT_SECONDS', 60)))
    max_tok = int(getattr(settings, 'CHAT_MAX_TOKENS', 700))

    all_messages = []
    if system_prompt:
        all_messages.append({'role': 'system', 'content': system_prompt})
    all_messages.extend(messages)

    return _post_nim(all_messages, model, max_tok, 0.25, timeout)
