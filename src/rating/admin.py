from django.contrib import admin
from .models import *


class TournamentAdmin(admin.ModelAdmin):
    list_display = ("id","title","end_datetime","start_datetime","typeoft")
    search_fields = ["title",]
    list_filter = ('typeoft',)
    #filter_horizontal = ['orgcommittee']
    raw_id_fields = ['orgcommittee']


class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "title",)
    search_fields = ["id", "title",]
    raw_id_fields = ['town']


class SyncrequestAdmin(admin.ModelAdmin):
    list_display = ("venue", "__town__")
    search_fields = ["venue",]


class RegionAdmin(admin.ModelAdmin):
    list_display = ("title", "country")
    search_fields = ["title",]


class TownAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "country")
    search_fields = ["title",]
    list_filter = ('country',)


class TypeoftAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ["title",]


class VenueAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "town")
    search_fields = ["title",]
    list_filter = ('town',)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "last_name","first_name", "patronymic")
    search_fields = ["last_name", "id"]


class OldratingAdmin(admin.ModelAdmin):
    list_display = ('__str__', '__date__', '__game__', 'rating', 'usedRating')
    search_fields = ["__str__",]
    raw_id_fields = ['player', 'result']


class NewratingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'game', 'team', 'mu', 'sigma', 'delta_mu',  'delta_sigma', 'rate')
    search_fields = ['player__last_name',]
    raw_id_fields = ['player', 'result']


class ReleaseratingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'mu', 'sigma', 'delta_mu',  'delta_sigma', 'rate')
    search_fields = ['player__last_name',]
    raw_id_fields = ['player', 'release']
    list_filter = ('release',)


class SquadAdmin(admin.ModelAdmin):
    list_display = ('team', 'date', 'mu', 'sigma', 'rate')
    search_fields = ['team__title',]
    raw_id_fields = ['team', 'release', 'teamMembers']
    list_filter = ('release',)


class OldteamratingAdmin(admin.ModelAdmin):
    list_display = ('__str__', '__date__', '__game__', 'inRating', 'b')
    search_fields = ["__str__",]
    #filter_horizontal = ['player', 'result']
    raw_id_fields = ['result']


class ResultAdmin(admin.ModelAdmin):
    list_display = ('tournament', '__date__', 'team', 'position', 'total', 'mask')
    search_fields = ["tournament","team"]
    raw_id_fields = ['team', 'tournament', 'teamMembers', 'syncrequest']


admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Country)
admin.site.register(Region, RegionAdmin)
admin.site.register(Town, TownAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Syncrequest, SyncrequestAdmin)
admin.site.register(Typeoft, TypeoftAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Oldrating, OldratingAdmin)
admin.site.register(Oldteamrating, OldteamratingAdmin)
