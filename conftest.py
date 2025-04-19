# conftest.py
import os
import environ

environ.Env.read_env()

env = environ.Env()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", env("DJANGO_SETTINGS_MODULE", default="config.django.test"))