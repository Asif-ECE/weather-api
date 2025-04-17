import os
import json
import subprocess
from django.conf import settings
from rest_framework.exceptions import APIException

_path = os.path.join(settings.BASE_DIR, 'data.json')
_districts = None
_districts_error = None

def load_districts():
    global _districts, _districts_error

    # If already loaded or failed, skip reloading
    if _districts or _districts_error:
        return

    if not os.path.exists(_path):
        try:
            result = subprocess.run(
                ['python', 'manage.py', 'fetch_json'],
                check=True,
                capture_output=True,
                text=True
            )
            
        except subprocess.CalledProcessError as e:
            _districts_error = RuntimeError(
                f"Fetch failed:\n{e.stdout}\n{e.stderr}"
            )
            return

    if not os.path.exists(_path):
        _districts_error = FileNotFoundError("data.json still missing after fetch attempt.")
        return

    try:
        with open(_path, 'r') as f:
            _districts = json.load(f)

            if not isinstance(_districts['districts'], list):
                raise ValueError("data.json does not contain a list.")
            if not isinstance(_districts['districts'][0], dict):
                raise ValueError("Each district should be a dictionary.")
    except json.JSONDecodeError as e:
        _districts_error = ValueError(f"Invalid JSON in data.json: {e}")


def get_districts():
    load_districts()

    if _districts_error:
        raise APIException(detail=_districts_error)
    return _districts['districts']