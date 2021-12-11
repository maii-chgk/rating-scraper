import requests
import json
import pytz
import tzlocal
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from honeybadger import honeybadger
from rating.models import *

honeybadger.configure(api_key=os.environ.get('HONEYBADGER_API_KEY'))


def get_town_venue(url):
    t_response = requests.get(url, timeout=10, headers={"accept":"application/json"})
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
    t_response = requests.get(url, timeout=10, headers={"accept":"application/json"})
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



def parse_tournaments(t_id, t_id_end, maii=False, force=False, date_diff=0):
    if maii:
        parse_range = []
        for j in range(1, 11, 1):
            maii_tournament_url = "http://api.rating.chgk.net/tournaments?properties.maiiRating=true&page=" + str(j)
            maii_tournament_response = requests.get(maii_tournament_url, timeout=10, headers={"accept":"application/json"})
            maii_tournament_data = json.loads(maii_tournament_response.text)
            for tournament in maii_tournament_data:
                parse_range.append(tournament['id'])
    elif date_diff > 0:
        time_from = (datetime.now()-timedelta(days=date_diff)).strftime("%Y-%m-%d")
        parse_range = []
        for j in range(1, 21, 1):
            tournament_url = "http://api.rating.chgk.net/tournaments?lastEditDate%5Bafter%5D="+time_from+"&page=" + str(j)
            tournament_response = requests.get(tournament_url, timeout=10, headers={"accept":"application/json"})
            tournament_data = json.loads(tournament_response.text)
            for tournament in tournament_data:
                parse_range.append(tournament['id'])
    else:
        parse_range = [*range(t_id, t_id_end+1, 1)]

    for i in parse_range:
        # парсим данные о турнире
        print("Парсим турнир:", i)
        tournament_url = "http://api.rating.chgk.net/tournaments/" + str(i)
        tournament_response = requests.get(tournament_url, timeout=10, headers={"accept":"application/json"})
        tournament_data = json.loads(tournament_response.text)

        # берём тип турнира, если в базе ещё нет - создаём
        try:
            typeoft = Typeoft.objects.filter(id=tournament_data['type']['id']).first()
        except TypeError:
            # ловим турниры которых нет на турнирном сайте, если мы парсим по диапазону и пропускаем отсутсвующий id
            continue

        # сравниваем дату обновления на турнирном сайте, с датой, которая у нас в базе
        local_timezone = tzlocal.get_localzone()
        end_datetime_to_compare = datetime.strptime(
            tournament_data['lastEditDate'], '%Y-%m-%dT%H:%M:%S%z'
            ).astimezone(local_timezone).replace(tzinfo=None)

        try:
            t_end_datetime_to_compare = Tournament.objects.filter(id=tournament_data['id']).first().edit_datetime
            if end_datetime_to_compare == t_end_datetime_to_compare and not force:
                # если турнир не обновлялся, пропускаем его
                print(tournament_data['name'], "- турнир не обновлялся")
                continue
        except AttributeError:
            # если турнир новый и его ещё нет у нас в базе, продолжаем flow
            pass

        if not typeoft:
            typeoft, is_updated = Typeoft.objects.update_or_create(
                id=tournament_data['type']['id'],
                defaults={
                    'title': tournament_data['type']['name'],
                },
            )

        # обновляем данные по самому турниру, кроме даты обновления, чтобы не получить неполные данные, если парсер прервется
        try:
            tournament, is_updated = Tournament.objects.update_or_create(
                id=tournament_data['id'],
                defaults={
                    'title': tournament_data['name'],
                    'start_datetime': tournament_data['dateStart'],
                    'end_datetime': tournament_data['dateEnd'],
                    'questionQty': json.dumps(tournament_data['questionQty']),
                    'typeoft': typeoft,
                    'maiiAegis': tournament_data['maiiAegis'],
                    'maii_rating': tournament_data['maiiRating'],
                    'maiiAegisUpdatedAt': tournament_data['maiiAegisUpdatedAt'],
                    'maiiRatingUpdatedAt': tournament_data['maiiRatingUpdatedAt']
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
        response = requests.get(url, timeout=20, headers={"accept":"application/json"})
        data = json.loads(response.text)

        # ищем не удалили ли результаты каких-то команд с турнирного сайта
        # берем результаты из своей базы
        db_results = list(Result.objects.filter(tournament=tournament).values_list('team__id',flat=True))
        # берем результаты отданные в API
        t_site_results = []
        for result in data:
            t_site_results.append(result['team']['id'])
        # смотрим что есть лишнего у нас
        diff_results = list(set(db_results) - set(t_site_results))
        # удаляем лишние результаты из базы
        Result.objects.filter(tournament=tournament, team__id__in=diff_results).delete()

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
                position = float(result['position'])
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

            # удаляем oldrating для игроков убранных из составов команд на турнирном сайте
            for oldrating in Oldrating.objects.filter(result=db_result):
                if oldrating.player not in db_result.teamMembers.all():
                    oldrating.delete()
            
            # фиксируем старый командный рейтинг для сравнения моделей в будущем
            inRating = False
            try:
                if result['rating']['inRating']:
                    inRating = True
            except TypeError:
                print(db_result.team_title, db_result.mask,db_result.total,db_result.position, "|", tournament, tournament.id)
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
            print(db_result.team_title, db_result.mask,db_result.total,db_result.position, "|", tournament, tournament.id)

        tournament.edit_datetime = tournament_data['lastEditDate']
        tournament.save()
        print("done: ", i)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-i', '--t_id', type=int)
        parser.add_argument('-e', '--t_id_end', type=int)
        parser.add_argument('--maii', action='store_true')
        parser.add_argument('--force', action='store_true')
        parser.add_argument('-d', '--date_diff', type=int)

    def handle(self, *args, **kwargs):
        maii = False
        force = False
        if kwargs["maii"]:
            maii = True
        if kwargs["force"]:
            force = True
        t_id = kwargs["t_id"]
        t_id_end = kwargs["t_id_end"]
        date_diff = kwargs["date_diff"]

        parse_tournaments(t_id, t_id_end, maii, force, date_diff)
