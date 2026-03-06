from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MatchEvent, Match
from django.db.models import Q

@receiver([post_save, post_delete], sender=MatchEvent)
def update_match_score(sender, instance, **kwargs):
    """
    The 'Brain': Every time an event is saved or deleted, 
    recalculate the score for the associated match.
    """
    match = instance.match
    
    # Logic for Home Team Goals
    # Includes: Home player scoring OR Away player scoring an Own Goal
    home_goals = MatchEvent.objects.filter(
        Q(match=match, event_type='GOAL', player__team=match.home_team) |
        Q(match=match, event_type='PENALTY', player__team=match.home_team) |
        Q(match=match, event_type='OWN_GOAL', player__team=match.away_team)
    ).count()

    # Logic for Away Team Goals
    # Includes: Away player scoring OR Home player scoring an Own Goal
    away_goals = MatchEvent.objects.filter(
        Q(match=match, event_type='GOAL', player__team=match.away_team) |
        Q(match=match, event_type='PENALTY', player__team=match.away_team) |
        Q(match=match, event_type='OWN_GOAL', player__team=match.home_team)
    ).count()

    # Update the match fields and save
    match.home_score = home_goals
    match.away_score = away_goals
    match.save()