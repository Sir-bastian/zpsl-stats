from django.contrib import admin
from django.db import models
from stats.models import MatchEvent, Player, Team, Match

# Inline models
class MatchEventInline(admin.TabularInline):
    model = MatchEvent
    extra = 1

    fields = ('event_type', 'minute', 'player', 'related_player')
    raw_id_fields = ('player', 'related_player')
    can_delete = True


class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'home_team', 'away_team', 'home_score', 'away_score', 'match_status')
    inlines = [MatchEventInline]

    readonly_fields = ('home_score', 'away_score')  # Scores should be updated via MatchEvent, not directly


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    # These fields can be seen but not edited in the Admin form
    readonly_fields = ('points', 'played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goal_difference')
    
    # Optional: organize the admin view so stats are at the bottom
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'city', 'logo', 'is_in_premier_league')}),
        ('Auto-Calculated Stats', {'fields': readonly_fields}),
    )

# Register your models here.
admin.site.register(Player)
admin.site.register(Match, MatchAdmin) 
admin.site.register(MatchEvent)


# Delete this later.
# This is just so I can work on mobile to recalculate Standings. 
from django.contrib import admin
from .services import update_team_standings

@admin.action(description='Recalculate selected teams stats')
def recalculate_stats(modeladmin, request, queryset):
    for team in queryset:
        update_team_standings(team)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'played', 'points')
    actions = [recalculate_stats] # This adds a dropdown option
