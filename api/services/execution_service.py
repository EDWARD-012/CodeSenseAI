"""
Code execution service for CodeSense AI.

Uses the public Judge0 API for remote code execution.
"""

import logging

import requests

logger = logging.getLogger(__name__)

JUDGE0_API_URL = 'https://ce.judge0.com/submissions?base64_encoded=false&wait=true'

LANGUAGE_MAP = {
    'python': 71,
    'javascript': 63,
    'typescript': 74,
    'bash': 46,
    'cpp': 54,
    'c': 50,
    'java': 62,
    'go': 60,
    'rust': 73,
    'csharp': 51,
    'ruby': 72,
    'php': 68,
}


def execute_code(code: str, language: str = 'python') -> dict:
    """Execute code remotely using the Judge0 API."""
    frontend_lang = language.lower().strip()
    language_id = LANGUAGE_MAP.get(frontend_lang)

    if not language_id:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Unsupported language for execution: {frontend_lang}.',
            'exit_code': -1,
            'timed_out': False,
            'language': frontend_lang,
        }

    try:
        logger.info('Sending code to Judge0 API (language_id: %s)', language_id)
        response = requests.post(
            JUDGE0_API_URL,
            json={'source_code': code, 'language_id': language_id},
            timeout=20,
        )
        response.raise_for_status()

        data = response.json()
        status_id = data.get('status', {}).get('id')
        stdout = data.get('stdout') or ''
        stderr = data.get('stderr') or ''
        compile_output = data.get('compile_output') or ''
        timed_out = status_id == 5

        if status_id == 6:
            stderr = f'Compilation Error:\n{compile_output}'
            exit_code = 1
        elif status_id and status_id >= 7:
            exit_code = 1
        else:
            exit_code = 0

        if not stdout and not stderr and data.get('message'):
            stderr = data.get('message')

        return {
            'success': exit_code == 0 and not timed_out,
            'stdout': stdout,
            'stderr': stderr,
            'exit_code': exit_code,
            'timed_out': timed_out,
            'language': frontend_lang,
        }

    except requests.exceptions.Timeout:
        logger.warning('Judge0 API request timed out.')
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Request to execution server timed out.',
            'exit_code': -1,
            'timed_out': True,
            'language': frontend_lang,
        }
    except Exception as exc:
        logger.exception('Judge0 API error: %s', exc)
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Execution server error. Please try again later.',
            'exit_code': -1,
            'timed_out': False,
            'language': frontend_lang,
        }
