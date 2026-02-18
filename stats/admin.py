from django.contrib import admin

from stats.models import Player, Standings, Teams, TopScorer

# Register your models here.
admin.site.register(Teams)
admin.site.register(Player)
admin.site.register(Standings) 
admin.site.register(TopScorer)