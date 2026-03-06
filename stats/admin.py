from django.contrib import admin
from django.db import models
from stats.models import MatchEvent, Player, Team, Match

# Inline models
class MatchEventInline(admin.TabularInline):
    model = MatchEvent
    extra = 1

    fields = ('event_type', 'minute', 'player', 'related_player')
    raw_id_fields = ('player', 'related_player')


class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'home_team', 'away_team', 'home_score', 'away_score', 'match_status')
    inlines = [MatchEventInline]

    readonly_fields = ('home_score', 'away_score')  # Scores should be updated via MatchEvent, not directly

# Register your models here.
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match, MatchAdmin) 
admin.site.register(MatchEvent)