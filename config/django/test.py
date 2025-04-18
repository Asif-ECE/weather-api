from .base import *

DEBUG = env.bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=["*"])

INSTALLED_APPS += [
    'silk',
    'drf_spectacular',
]

MIDDLEWARE = ['silk.middleware.SilkyMiddleware'] + MIDDLEWARE

SPECTACULAR_SETTINGS = {
    'TITLE': 'Weather API',
    'DESCRIPTION': 'Travel Recommendation based on weather and air quality.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}