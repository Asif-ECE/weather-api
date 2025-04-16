import os
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from config.django.base import env

class Command(BaseCommand):
    help = 'Fetches JSON data from URL and saves it to a local file'

    def handle(self, *args, **kwargs):
        url = env('DISTRICT_DATA_URL')
        local_path = os.path.join(settings.BASE_DIR, 'data.json')  # Saves to project root

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            with open(local_path, 'w') as f:
                json.dump(data, f, indent=2)

            self.stdout.write(self.style.SUCCESS(f"JSON data saved to {local_path}"))
        except Exception as e:
            self.stderr.write(f"Error fetching or saving JSON: {e}")
