# apps/core/context_processors.py
from django.conf import settings

def global_settings(request):
    """Provide global settings/data to all templates."""
    return {
        'SITE_NAME': 'منصة ارتقاء التعليمية',
        'SITE_URL': request.build_absolute_uri('/'),
        # Add any other global variables needed in base.html
    }
