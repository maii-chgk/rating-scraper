import requests
import json
from django.core.management.base import BaseCommand
from rating.models import *


def parse_squads(start, end):
    parse_range = [*range(start, end+1, 1)]
    for i in parse_range:
        # парсим данные о турнире
        print("Парсим игрока:", i)
        player = Player.objects.filter(id=i).first()
        if not player:
            print("Игрока не существует")
            continue

        url = "https://rating.chgk.info/api/players/" + str(i) + "/teams"
        response = requests.get(url, timeout=10)
        data = json.loads(response.text)
        for season in data:
            try:
                basesquad, is_updated = Basesquad.objects.update_or_create(
                    season_id = season['idseason'],
                    team_id = season['idteam'],
                    player = player,
                    defaults={
                        'iscaptain': season['is_captain'],
                        'start_date': season['added_since'],
                    },
                )
            except:
                print("Нет сыгранных турниров, пропускаем:", season['idseason'])
        print("Распарсили игрока:", i)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-s", "--start", type=int)
        parser.add_argument("-e", "--end", type=int)


    def handle(self, *args, **kwargs):
        start = kwargs["start"]
        end = kwargs["end"]
        parse_squads(start, end)
