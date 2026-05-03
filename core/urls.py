"""
Root URL configuration for CodeSense AI.

Routes:
  /          -> Main app page (Django template)
  /api/      -> API endpoints (review-code, chat, run-code)
"""

from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Frontend page
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    # API routes
    path('api/', include('api.urls')),
]
