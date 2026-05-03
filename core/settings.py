"""
Django settings for CodeSense AI - AI Code Reviewer.

Configurable via environment variables for local development and Vercel deployment.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-key-change-in-production-!@#$%'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() == 'true'

ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    '*'
).split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Minimal database for Django test runner compatibility
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Application Configuration ---

# Ollama settings
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen2.5-coder')

# RAG settings
ENABLE_RAG = os.environ.get('ENABLE_RAG', 'true').lower() == 'true'

# Input limits
MAX_CODE_CHARS = int(os.environ.get('MAX_CODE_CHARS', '20000'))

# Request timeout (seconds)
REQUEST_TIMEOUT_SECONDS = int(os.environ.get('REQUEST_TIMEOUT_SECONDS', '120'))

# Supported languages
SUPPORTED_LANGUAGES = [
    'python', 'javascript', 'typescript', 'java', 'c', 'cpp',
    'csharp', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin',
    'html', 'css', 'sql', 'bash', 'powershell', 'other'
]

# Supported review modes
SUPPORTED_REVIEW_MODES = [
    'general', 'bugs', 'security', 'performance', 'style', 'explain'
]
