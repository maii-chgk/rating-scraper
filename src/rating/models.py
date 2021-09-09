from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
import json
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
from django.db.models import JSONField

#############################
# модели для данных, собираемых с турнирного сайта raiting.chgk.info
#############################

class Country(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Region(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Town(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# площадки
class Venue(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    town = models.ForeignKey(Town, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# заявки на проведение
class Syncrequest(models.Model):
    id = models.IntegerField(primary_key=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    def __str__(self):
        return self.venue.title

    def __town__(self):
        return self.venue.town


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, default='', blank=True, null=True)
    last_name = models.CharField(max_length=100)
    

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=250)
    town = models.ForeignKey(Town, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.title


class Season(models.Model):
    id = models.IntegerField(primary_key=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ('-end',)

    def __str__(self):
        return str(self.id)


class Basesquad(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    iscaptain = models.BooleanField(default=False)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)

    class Meta:
        unique_together = [['season', 'team', 'player']]
        ordering = ('-season__id',)

    def __str__(self):
        return self.team.title + ' ' + str(self.season.id)



# типы турниров
class Typeoft(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Tournament(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    typeoft = models.ForeignKey(Typeoft, on_delete=models.CASCADE)
    orgcommittee = models.ManyToManyField(Player)
    questionQty = JSONField(null=True, default=dict)
    teams = models.IntegerField(default=0)
    maiiAegis = models.BooleanField(default=False)
    maiiAegisUpdatedAt = models.DateTimeField(null=True)
    maiiRating = models.BooleanField(default=False)
    maiiRatingUpdatedAt = models.DateTimeField(null=True)


    class Meta:
        ordering = ('-end_datetime', '-start_datetime', '-id')

    def __str__(self):
        return self.title


class Flag(models.Model):
    id = models.IntegerField(primary_key=True)
    shortName = models.CharField(max_length=100)
    longName = models.CharField(max_length=100)

    def __str__(self):
        return self.longName

class Result(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    mask = ArrayField(models.CharField(max_length=2, default=''), default=list)
    flags = models.ManyToManyField(Flag)
    team_title = models.CharField(max_length=250)
    total = models.IntegerField(default=0)
    syncrequest = models.ForeignKey(Syncrequest, on_delete=models.CASCADE, null=True, blank=True)
    position = models.DecimalField(max_digits=5, decimal_places=1)
    teamMembers = models.ManyToManyField(Player)
    composite_mu = models.FloatField(default=0)
    composite_sigma = models.FloatField(default=0)
    winrate = models.FloatField(default=0)
    teams_on = models.IntegerField(default=0)
    

    class Meta:
        unique_together = [['team', 'tournament']]
        ordering = ('-tournament__end_datetime', '-tournament__start_datetime', '-tournament__id', '-total')

    def __str__(self):
        return self.team.title

    def __date__(self):
        return self.tournament.end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def rate(self):
        return self.composite_mu - self.composite_sigma*3


# Рейтинг игроков использованный при расчете бонусов в турнире
class Oldrating(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    usedRating = models.IntegerField(default=0)
    flag = models.CharField(max_length=50, default='', null=True)

    class Meta:
        unique_together = [['player', 'result']]
        ordering = ('-result__tournament__end_datetime', '-result__tournament__start_datetime', '-result__tournament__id')

    def __str__(self):
        return self.player.first_name + ' ' + self.player.last_name

    def __date__(self):
        return self.result.tournament.end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def __game__(self):
        return self.result.tournament.title


# Рейтинг команд рассчитаный по результатам турнира
class Oldteamrating(models.Model):
    result = models.OneToOneField(
        Result,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    inRating = models.BooleanField(default=True)
    b = models.IntegerField(default=0)
    predictedPosition = models.IntegerField(default=0)
    rt = models.IntegerField(default=0)
    rb = models.IntegerField(default=0)
    rg = models.IntegerField(default=0)
    r = models.CharField(max_length=50, default='')
    bp = models.IntegerField(default=0)
    d1 = models.IntegerField(default=0)
    d2 = models.IntegerField(default=0)
    d = models.IntegerField(default=0)

    class Meta:
        ordering = ('-result__tournament__end_datetime', '-result__tournament__start_datetime', '-result__tournament__id')

    def __str__(self):
        return self.result.team.title

    def __date__(self):
        return self.result.tournament.end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def __game__(self):
        return self.result.tournament.title


