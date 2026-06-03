"""
API URL routes for CodeSense AI.

Endpoints:
  POST /api/login        -> JWT login
  POST /api/review-code  -> AI code review
  POST /api/chat         -> Follow-up chat
  POST /api/run-code     -> Reserved (disabled)
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('login', views.login, name='login'),
    path('review-code', views.review_code, name='review_code'),
    path('chat', views.chat, name='chat'),
    path('run-code', views.run_code, name='run_code'),
]
