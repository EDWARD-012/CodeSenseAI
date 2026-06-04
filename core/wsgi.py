"""
WSGI config for CodeSense AI.

Runs Django migrations automatically on Vercel startup
so that auth tables always exist in /tmp/db.sqlite3.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# Auto-migrate on Vercel (fresh /tmp db on every cold start)
try:
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
except Exception:
    pass  # Never crash WSGI startup

app = application  # Required by Vercel
