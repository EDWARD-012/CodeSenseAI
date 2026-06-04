"""
Code execution service for CodeSense AI (Cloud/Vercel Ready).

Uses the public Judge0 API (https://ce.judge0.com) 
for secure, remote code execution.
"""

import requests
import logging

logger = logging.getLogger(__name__)

# Judge0 execution endpoint
JUDGE0_API_URL = 'https://ce.judge0.com/submissions?base64_encoded=false&wait=true'

# Map frontend language names to Judge0 language IDs
LANGUAGE_MAP = {
    'python': 71,       # Python (3.8.1)
    'javascript': 63,   # Node.js (12.14.0)
    'typescript': 74,   # TypeScript (3.7.4)
    'bash': 46,         # Bash (5.0.0)
    'cpp': 54,          # C++ (GCC 9.2.0)
    'c': 50,            # C (GCC 9.2.0)
    'java': 62,         # Java (OpenJDK 13.0.1)
    'go': 60,           # Go (1.13.5)
    'rust': 73,         # Rust (1.40.0)
    'csharp': 51,       # C# (Mono 6.6.0.161)
    'ruby': 72,         # Ruby (2.7.0)
    'php': 68,          # PHP (7.4.1)
}


def execute_code(code: str, language: str = 'python', stdin: str = '') -> dict:
    """
    Execute code remotely using the Judge0 API.
    """
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

    payload = {
        'source_code': code,
        'language_id': language_id,
        'stdin': stdin,
    }

    try:
        logger.info(f'Sending code to Judge0 API (language_id: {language_id})')
        response = requests.post(JUDGE0_API_URL, json=payload, timeout=20)
        response.raise_for_status()

        data = response.json()
        
        # Judge0 status IDs: 3 = Accepted, 4 = Wrong Answer, 5 = Time Limit Exceeded, 6 = Compilation Error
        # 7-12 = Runtime Error
        status_id = data.get('status', {}).get('id')
        
        stdout = data.get('stdout') or ''
        stderr = data.get('stderr') or ''
        compile_output = data.get('compile_output') or ''
        
        timed_out = status_id == 5
        
        # If compilation failed, put it in stderr
        if status_id == 6:
            stderr = f"❌ Compilation Error:\n{compile_output}"
            exit_code = 1
        elif status_id >= 7:
            exit_code = 1
        else:
            exit_code = 0

        # Sometimes errors are in message
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
            'stderr': '⏱️ Request to execution server timed out.',
            'exit_code': -1,
            'timed_out': True,
            'language': frontend_lang,
        }
    except Exception as e:
        logger.exception(f'Judge0 API error: {e}')
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Execution server error. Please try again later.',
            'exit_code': -1,
            'timed_out': False,
            'language': frontend_lang,
        }
