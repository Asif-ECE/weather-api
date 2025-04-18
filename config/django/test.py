from .base import *

EBUG = env.bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=["*"])

INSTALLED_APPS += [
    'silk',
]

MIDDLEWARE = ['silk.middleware.SilkyMiddleware'] + MIDDLEWARE