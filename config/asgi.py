"""
ASGI config for WeatherAPI project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from .django.base import env

from django.core.asgi import get_asgi_application

os.environ.setdefault(env('DJANGO_SETTINGS_MODULE'), 'config.django.dev')

application = get_asgi_application()
