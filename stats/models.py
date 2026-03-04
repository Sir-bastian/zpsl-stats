from datetime import date

from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    founded_year = models.IntegerField()
    homeground = models.CharField(max_length=100)
    is_in_premier_league = models.BooleanField(default=True)

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
            'points': 0,
            'win_percentage': 0
        }
        
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

        ''' Logic to calculate recent form - last 5 matches. Can be used to show 
        form in standings page and also for future features like form-based predictions.
        Points show you the Past, Form can tell you the Future'''
        recent_matches = all_matches.order_by('-date')[:5]
        recentForm = []
        for match in recent_matches:
            if match.home_team == self:
                if match.home_score > match.away_score:
                    recentForm.append('W')
                elif match.home_score < match.away_score:
                    recentForm.append('L')
                else:
                    recentForm.append('D')
            else:
                if match.away_score > match.home_score:
                    recentForm.append('W')
                elif match.away_score < match.home_score:
                    recentForm.append('L')
                else:
                    recentForm.append('D')
        
        stats['form'] = recentForm[::-1]  # Reverse to show most recent form first
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
        stats['win_percentage'] = stats['wins'] / stats['played'] * 100 if stats['played'] > 0 else 0
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

    @property
    def goal_difference(self):
        return self.stats['goal_difference']

    @property
    def win_percentage(self):
        return self.stats['win_percentage']
    
    @property
    def form(self):
        return self.stats['form']

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    position = models.CharField(max_length=50)
    age = models.IntegerField()

    def __str__(self):
        return (
            f"Player: {self.name}, Team: {self.team.name}, "
            f"Position: {self.position}, Age: {self.age}"
        )

class Match(models.Model):
    ''' Model to represent a football match between two teams. It captures essential 
    details like date, time, venue, teams involved, scores and match status.
    This model can be used to display match schedules, results, and also for future 
    features like match predictions, head-to-head stats, and detailed match reports.'''
    class MatchStatus(models.TextChoices):
        '''Using TextChoices to define match status options for better data integrity and readability'''
        Completed = 'FINISHED', 'Finished'
        UPCOMING = 'SCHEDULED', 'Scheduled'
        LIVE = 'IN_PLAY', 'Live'

    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.PROTECT)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.PROTECT)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    match_status = models.CharField(
        max_length=20,
        choices=MatchStatus.choices,
        default=MatchStatus.Completed
    )

    def __str__(self):
        return (
            f"Match: {self.home_team.name} vs {self.away_team.name} on {self.date} at {self.time} at {self.venue} - Status: {self.match_status}"
        )
    

class MatchEvent(models.Model):
    ''' Model to capture key events in a match like goals, assists, cards, substitutions etc.
    This can be used to show detailed match reports and also for future features like player 
    stats, top scorers, assist leaders, disciplinary records etc.'''
    class EventType(models.TextChoices):
        GOAL = 'GOAL', 'Goal'
        ASSIST = 'ASSIST', 'Assist'
        YELLOW_CARD = 'YELLOW', 'Yellow Card'
        RED_CARD = 'RED', 'Red Card'
        OWN_GOAL = 'OWN_GOAL', 'Own Goal'
        SUBSTITUTION = 'SUB', 'Substitution'
        PENALTY = 'PENALTY', 'Penalty'

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='match_events')
    # Optional: for assists or substitutions
    related_player = models.ForeignKey(
        Player, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='related_match_events'
    )
    
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.GOAL
    )
    minute = models.PositiveIntegerField()

    class Meta:
        ordering = ['minute'] # Always sort events by time by default

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.player.name} ({self.minute}')"