from .models import Team, Match

def update_team_standings(team):
    """
    Recalculates and saves the stats for a single team based on all finished matches.
    """
    stats = team.get_stats() # Use your existing logic!
    
    team.played = stats['played']
    team.wins = stats['wins']
    team.draws = stats['draws']
    team.losses = stats['losses']
    team.goals_for = stats['goals_for']
    team.goals_against = stats['goals_against']
    team.goal_difference = stats['goal_difference']
    team.points = stats['points']
    
    team.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import update_team_standings

@receiver(post_save, sender=Match)
def match_post_save(sender, instance, **kwargs):
    # Only update if the match is finished
    if instance.match_status == 'FINISHED':
        update_team_standings(instance.home_team)
        update_team_standings(instance.away_team)