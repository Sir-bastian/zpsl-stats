from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    founded_year = models.IntegerField()
    homeground = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    
    ''' Logic for caluculating wins, losses, draws, Goals for a team
     Data cn be later used to calculate points and standings in the league table '''
    def get_stats(self):
        all_matches = Match.objects.filter(
            Q(home_team=self) | Q(away_team=self),
            match_status='Completed')
        
        stats = {
            'played': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0,
            'points': 0}
        
        for match in all_matches:
            stats['played'] += 1
            #Logic for when self is home team.
            if match.home_team == self:
                stats['goals_for'] += match.home_score
                stats['goals_against'] += match.away_score
                if match.home_score > match.away_score:
                    stats['wins'] += 1
                    stats['points'] += 3
                elif match.home_score < match.away_score:
                    stats['losses'] += 1
                else:
                    stats['draws'] += 1
                    stats['points'] += 1
            #Logic for when self is away team.        
            else:
                stats['goals_for'] += match.away_score
                stats['goals_against'] += match.home_score
                if match.away_score > match.home_score:
                    stats['wins'] += 1
                    stats['points'] += 3
                elif match.away_score < match.home_score:
                    stats['losses'] += 1
                else:
                    stats['draws'] += 1
                    stats['points'] += 1

        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
        return stats
    
    @cached_property
    def stats(self):
        """
        The "Memory Bank": Django runs get_stats() the first time 
        you ask for a stat, then remembers it for the rest of the page load.
        """
        return self.get_stats()
    
    @property
    def points(self):
        return self.stats['points']

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.CharField(max_length=50)
    age = models.IntegerField()

    def __str__(self):
        return (
            f"Player: {self.name}, Team: {self.team.name}, "
            f"Position: {self.position}, Age: {self.age}"
        )

class Match(models.Model):
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    match_status = models.TextField() # e.g., Scheduled, Ongoing/Live, Completed.

    def __str__(self):
        return (
            f"Match: {self.home_team.name} vs {self.away_team.name} on {self.date} at {self.time} at {self.venue} - Status: {self.match_status}"
        )
    

class MatchEvents(models.Model):
    class EventType(models.TextChoices):
        GOAL = 'Goal', 'Goal'
        ASSIST = 'Assist', 'Assist'
        YELLOW_CARD = 'Yellow Card', 'Yellow Card'
        RED_CARD = 'Red Card', 'Red Card'
        OWN_GOAL = 'Own Goal', 'Own Goal'

    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event_type = models.CharField(
        max_length = 50,
        choices = EventType.choices,
        default = EventType.GOAL
        )
    minute = models.PositiveIntegerField()  # Minute of the match when the event occurred

    def __str__(self):
        return (
            f"Event: {self.event_type} by {self.player.name} in {self.minute} minute of match {self.match}"
        )