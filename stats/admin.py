from django.contrib import admin
from django.db import models
from stats.models import MatchEvent, Player, Team, Match
from .services import update_team_standings

# Inline models
class MatchEventInline(admin.TabularInline):
    model = MatchEvent
    extra = 1

    fields = ('event_type', 'minute', 'player', 'related_player')
    raw_id_fields = ('player', 'related_player')
    can_delete = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['player', 'related_player']:
           # Extract the current Match ID from the Admin change view URL context
           resolved = request.resolver_match
           match_id = resolved.kwargs.get('object_id') if resolved else None
        
        if match_id:
            try:
                # Fetch the current match instance
                match = Match.objects.get(pk=match_id)
                # Filter players belonging to either the home team or the away team
                kwargs['queryset'] = db_field.remote_field.model.objects.filter(
                    team__in=[match.home_team, match.away_team]
                ).distinct()
            except Match.DoesNotExist:
                # Fallback to an empty queryset if the match object cannot be found
                kwargs['queryset'] = db_field.remote_field.model.objects.none()
        else:
            # Fallback for "Add" view where the Match object does not exist yet
            kwargs['queryset'] = db_field.remote_field.model.objects.none()

    return super().formfield_for_foreignkey(db_field, request, **kwargs)

class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'home_team', 'away_team', 'home_score', 'away_score', 'match_status')
    inlines = [MatchEventInline]

    readonly_fields = ('home_score', 'away_score')  # Scores should be updated via MatchEvent, not directly

@admin.action(description='Recalculate selected teams stats')
def recalculate_stats(modeladmin, request, queryset):
    # This functions is a button which handles reCalculate stats in admin Panel
    for team in queryset:
        update_team_standings(team)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    # These fields can be seen but not edited in the Admin form
    readonly_fields = ('points', 'played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goal_difference')
    
    # Optional: organize the admin view so stats are at the bottom
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'city', 'logo', 'is_in_premier_league')}),
        ('Auto-Calculated Stats', {'fields': readonly_fields}),
    )
    actions = [recalculate_stats]

# Register your models here.
admin.site.register(Player)
admin.site.register(Match, MatchAdmin) 
admin.site.register(MatchEvent)