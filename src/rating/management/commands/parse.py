import requests
import json
from django.core.management.base import BaseCommand
from rating.models import *


def get_town_venue(url):
    t_response = requests.get(url)
    t_data = json.loads(t_response.text)['town']

    # проверяем есть ли у нас в базе страна команды
    country = Country.objects.filter(id=t_data['country']['id']).first()
    if not country:
        country, is_updated = Country.objects.update_or_create(
            id=t_data['country']['id'],
            defaults={
                'title': t_data['country']['name']
            },
        )

    # регион
    try:
        region = Region.objects.filter(id=t_data['region']['id']).first()
        if not region:
            region, is_updated = Region.objects.update_or_create(
                id=t_data['region']['id'],
                defaults={
                    'title': t_data['region']['name'],
                    'country': country
                },
            )
    except TypeError:
        region = None

    # город
    town = Town.objects.filter(id=t_data['id']).first()
    if not town:
        town, is_updated = Town.objects.update_or_create(
            id=t_data['id'],
            defaults={
                'title': t_data['name'],
                'country': country,
                'region': region,
            },
        )
    return town


def get_town(url):
    t_response = requests.get(url)
    t_data = json.loads(t_response.text)

    # проверяем есть ли у нас в базе страна команды
    country = Country.objects.filter(id=t_data['country']['id']).first()
    if not country:
        country, is_updated = Country.objects.update_or_create(
            id=t_data['country']['id'],
            defaults={
                'title': t_data['country']['name']
            },
        )

    # регион
    try:
        region = Region.objects.filter(id=t_data['region']['id']).first()
        if not region:
            region, is_updated = Region.objects.update_or_create(
                id=t_data['region']['id'],
                defaults={
                    'title': t_data['region']['name'],
                    'country': country
                },
            )
    except TypeError:
        region = None

    # город
    town = Town.objects.filter(id=t_data['id']).first()
    if not town:
        town, is_updated = Town.objects.update_or_create(
            id=t_data['id'],
            defaults={
                'title': t_data['name'],
                'country': country,
                'region': region,
            },
        )
    return town



def parse_tournaments(t_id, t_id_end):
    for i in range (t_id, t_id_end+1, 1):
        # парсим данные о турнире
        print("Парсим турнир:", i)
        tournament_url = "http://api.rating.chgk.net/tournaments/" + str(i)
        tournament_response = requests.get(tournament_url)
        tournament_data = json.loads(tournament_response.text)

        # берём тип турнира, если в базе ещё нет - создаём

        try:
            typeoft = Typeoft.objects.filter(id=tournament_data['type']['id']).first()
        except TypeError:
            continue
        if not typeoft:
            typeoft, is_updated = Typeoft.objects.update_or_create(
                id=tournament_data['type']['id'],
                defaults={
                    'title': tournament_data['type']['name'],
                },
            )

        # обновляем данные по самому турниру
        try:
            tournament, is_updated = Tournament.objects.update_or_create(
                id=tournament_data['id'],
                defaults={
                    'title': tournament_data['name'],
                    'start_datetime': tournament_data['dateStart'],
                    'end_datetime': tournament_data['dateEnd'],
                    'questionQty': json.dumps(tournament_data['questionQty']),
                    'typeoft': typeoft,
                },
            )
        except Exception as e:
            continue
        # парсим оргномитет турнира, линкуем
        tournament.orgcommittee.clear()
        for org in tournament_data['orgcommittee']:
            player, is_updated = Player.objects.update_or_create(
                id=org['id'],
                defaults={
                    'first_name': org['name'],
                    'last_name': org['surname'],
                    'patronymic': org['patronymic'],
                },
            )
            tournament.orgcommittee.add(player)

        print("Турнир сохранен")

        # парсим результаты турнира
        url = "http://api.rating.chgk.net/tournaments/" + str(i) +"/results?includeTeamMembers=1&includeMasksAndControversials=1&includeTeamFlags=1&includeRatingB=1"
        response = requests.get(url)
        data = json.loads(response.text)
        for result in data:
            # тянем информация о городе
            try:
                t_url = "http://api.rating.chgk.net/towns/" + str(result['team']['town']['id'])
                town = get_town(t_url)
            except TypeError:
                town = None
            # для каждого результата создаём команду
            team, is_updated = Team.objects.update_or_create(
                id=result['team']['id'],
                defaults={
                    'title': result['team']['name'],
                    'town': town
                },
            )

            # данные о площадке
            try:
                v_url = "http://api.rating.chgk.net/venues/" + str(result['synchRequest']['venue']['id'])
                town = get_town_venue(v_url)
                venue = Venue.objects.filter(id=result['synchRequest']['venue']['id']).first()
                if not venue:
                    venue, is_updated = Venue.objects.update_or_create(
                        id=result['synchRequest']['venue']['id'],
                        defaults={
                            'title': result['synchRequest']['venue']['name'],
                            'town': town,
                        },
                    )
            except TypeError:
                venue = None

            try:
                syncrequest = Syncrequest.objects.filter(id=result['synchRequest']['id']).first()
                if not syncrequest:
                    syncrequest, is_updated = Syncrequest.objects.update_or_create(
                        id=result['synchRequest']['id'],
                        defaults={
                            'venue': venue,
                        },
                    )
            except TypeError:
                syncrequest = None

            # апдейтим результат
            try:
                mask = list(result['mask'])
            except TypeError:
                mask = []
            try:
                total = int(result['questionsTotal'])
            except TypeError:
                total = 0
            try:
                position = int(result['position'])
            except TypeError:
                position = 0
            db_result, is_updated = Result.objects.update_or_create(
                team=team, tournament=tournament,
                defaults={
                    'mask': mask,
                    'team_title': result['current']['name'],
                    'total': total,
                    'syncrequest': syncrequest,
                    'position': position,
                },
            )
            # прописываем флаги
            db_result.flags.clear()
            for flag in result['flags']:
                db_flag, is_updated = Flag.objects.update_or_create(
                    id=flag['id'],
                    defaults={
                        'shortName': flag['shortName'],
                        'longName': flag['longName'],
                    },
                )
                db_result.flags.add(db_flag)

            # создаём или апдейтим игроков, пишем их старые индивидуальные рейтинги для сравнения моделей в будущем
            db_result.teamMembers.clear()
            for teammember in result['teamMembers']:
                player, is_updated = Player.objects.update_or_create(
                    id=teammember['player']['id'],
                    defaults={
                        'first_name': teammember['player']['name'],
                        'last_name': teammember['player']['surname'],
                        'patronymic': teammember['player']['patronymic'],
                    },
                )
                db_result.teamMembers.add(player)

                oldrating, is_updated = Oldrating.objects.update_or_create(
                    player=player, result=db_result,
                    defaults={
                        'rating': teammember['rating'],
                        'usedRating': teammember['usedRating'],
                        'flag': teammember['flag'],
                    },
                )
            # фиксируем старый командный рейтинг для сравнения моделей в будущем
            inRating = False
            try:
                if result['rating']['inRating']:
                    inRating = True
            except TypeError:
                continue
            rating, is_updated = Oldteamrating.objects.update_or_create(
                result=db_result,
                defaults={
                    'inRating': inRating,
                    'b': result['rating']['b'],
                    'predictedPosition': result['rating']['predictedPosition'],
                    'rt': result['rating']['rt'],
                    'rb': result['rating']['rb'],
                    'rg': result['rating']['rg'],
                    'r': result['rating']['r'],
                    'bp': result['rating']['bp'],
                    'd1': result['rating']['d1'],
                    'd2': result['rating']['d2'],
                    'd': result['rating']['d'],
                },
            )

            print(team, "|", tournament, tournament.id)
        print("done: ", i)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-i", "--t_id", type=int)
        parser.add_argument("-e", "--t_id_end", type=int)

    def handle(self, *args, **kwargs):
        t_id = kwargs["t_id"]
        t_id_end = kwargs["t_id_end"]
        parse_tournaments(t_id, t_id_end)