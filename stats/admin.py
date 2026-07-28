from django.contrib import admin
from django.db.models import Q
from stats.models import MatchEvent, Player, Team, Match
from .services import update_team_standings

# Inline models

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    # search functionality used by the autocomplete bars
    search_fields = ['name', 'team__name']
    list_display = ['name', 'team', 'position', 'age']

class MatchEventInline(admin.TabularInline):
    model = MatchEvent
    extra = 1

    fields = ['event_type', 'minute', 'player', 'related_player']
    autocomplete_fields = ['player', 'related_player']
    can_delete = True

    def formfield_for_foreignkey(self, db_field, request, obj=None, **kwargs):
        # Obj is the instance of the parent model (Match) being edited. We can use it to filter the players based on the teams in the match.
        if db_field.name in ["player", "related_player"] and obj:
            # Filter players to only those in the home or away team of the match.
            kwargs["queryset"] = Player.objects.filter(
                Q(team=obj.home_team) | Q(team=obj.away_team)
            )
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

admin.site.register(Match, MatchAdmin) 
admin.site.register(MatchEvent)