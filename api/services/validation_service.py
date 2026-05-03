"""
Validation service for CodeSense AI.

Validates incoming request payloads for code review and chat endpoints.
"""

from django.conf import settings


def validate_review_request(data: dict) -> tuple[bool, str | None]:
    """
    Validate the code review request payload.

    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message is None.
    """
    # Check code exists
    code = data.get('code', '').strip()
    if not code:
        return False, 'Code is required. Please provide source code to review.'

    # Check code length
    max_chars = getattr(settings, 'MAX_CODE_CHARS', 20000)
    if len(code) > max_chars:
        return False, f'Code exceeds maximum length of {max_chars} characters.'

    # Check language
    language = data.get('language', '').lower().strip()
    supported = getattr(settings, 'SUPPORTED_LANGUAGES', [])
    if language and supported and language not in supported:
        return False, f'Unsupported language: {language}. Supported: {", ".join(supported)}'

    # Check review mode
    review_mode = data.get('reviewMode', '').lower().strip()
    supported_modes = getattr(settings, 'SUPPORTED_REVIEW_MODES', [])
    if review_mode and supported_modes and review_mode not in supported_modes:
        return False, f'Unsupported review mode: {review_mode}. Supported: {", ".join(supported_modes)}'

    return True, None


def validate_chat_request(data: dict) -> tuple[bool, str | None]:
    """
    Validate the chat request payload.

    Returns:
        Tuple of (is_valid, error_message).
    """
    message = data.get('message', '').strip()
    if not message:
        return False, 'Message is required.'

    if len(message) > 5000:
        return False, 'Message is too long. Maximum 5000 characters.'

    return True, None
