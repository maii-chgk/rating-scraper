import requests
import json
from django.core.management.base import BaseCommand
from rating.models import *


def parse():
    # парсим сезоны

    url = "http://api.rating.chgk.net/seasons"
    response = requests.get(url, timeout=10)
    data = json.loads(response.text)

    for season_data in data:
        print(season_data)
        season, is_updated = Season.objects.update_or_create(
            id=season_data['id'],
            defaults={
                'start': season_data['dateStart'],
                'end': season_data['dateEnd'],
            },
        )

class Command(BaseCommand):
    def handle(self, *args, **kwargs):        
        parse()
