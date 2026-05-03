"""
LLM service for CodeSense AI (NVIDIA NIM / OpenAI Compatible).

Handles HTTP communication with the NVIDIA NIM API.
Replaces the old Ollama local setup for cloud deployment.
"""

import json
import logging
import requests
import os
from django.conf import settings

logger = logging.getLogger(__name__)


class OllamaServiceError(Exception):
    """Raised when LLM API communication fails (kept name for backward compatibility)."""
    pass


def _get_api_key():
    key = getattr(settings, 'NVIDIA_API_KEY', os.environ.get('NVIDIA_API_KEY'))
    if not key or key == 'put_your_key_here':
        raise OllamaServiceError('NVIDIA_API_KEY is not configured in environment variables.')
    return key


def generate(prompt: str, system_prompt: str = '') -> str:
    """
    Call Nvidia NIM chat/completions API for single-turn generation.
    """
    api_key = _get_api_key()
    model = getattr(settings, 'LLM_MODEL', os.environ.get('LLM_MODEL', 'meta/llama-3.1-70b-instruct'))
    timeout = getattr(settings, 'REQUEST_TIMEOUT_SECONDS', 120)

    url = 'https://integrate.api.nvidia.com/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})

    payload = {
        'model': model,
        'messages': messages,
        'temperature': 0.2,
        'max_tokens': 2048,
        'stream': False,
    }

    try:
        logger.info(f'Calling NVIDIA NIM API with model={model}')
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()

        result = response.json()
        generated_text = result['choices'][0]['message']['content']

        if not generated_text:
            raise OllamaServiceError('AI returned an empty response.')

        return generated_text

    except requests.exceptions.Timeout:
        logger.error(f'NVIDIA API timed out after {timeout}s')
        raise OllamaServiceError('AI response timed out. Please try again.')
    except requests.exceptions.HTTPError as e:
        logger.error(f'NVIDIA HTTP error: {e.response.text}')
        raise OllamaServiceError(f'AI server error: {e.response.status_code} - {e.response.reason}')
    except Exception as e:
        logger.exception(f'Failed to parse AI response: {e}')
        raise OllamaServiceError('Failed to process AI response.')


def chat(messages: list[dict], system_prompt: str = '') -> str:
    """
    Call Nvidia NIM chat/completions API for multi-turn conversation.
    """
    api_key = _get_api_key()
    model = getattr(settings, 'LLM_MODEL', os.environ.get('LLM_MODEL', 'meta/llama-3.1-70b-instruct'))
    timeout = getattr(settings, 'REQUEST_TIMEOUT_SECONDS', 120)

    url = 'https://integrate.api.nvidia.com/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    all_messages = []
    if system_prompt:
        all_messages.append({'role': 'system', 'content': system_prompt})
    all_messages.extend(messages)

    payload = {
        'model': model,
        'messages': all_messages,
        'temperature': 0.5,
        'max_tokens': 1024,
        'stream': False,
    }

    try:
        logger.info(f'Calling NVIDIA NIM chat API with model={model}')
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        if not content:
            raise OllamaServiceError('AI returned an empty chat response.')

        return content

    except requests.exceptions.HTTPError as e:
        logger.error(f'NVIDIA HTTP error: {e.response.text}')
        raise OllamaServiceError(f'AI server error: {e.response.status_code}')
    except Exception as e:
        logger.exception(f'Failed to parse AI response: {e}')
        raise OllamaServiceError('Failed to process AI chat response.')
