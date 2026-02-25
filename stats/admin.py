from django.contrib import admin

from stats.models import MatchEvents, Player, Team, Match

# Register your models here.
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match) 
admin.site.register(MatchEvents)