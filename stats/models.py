from datetime import date

from django.db import models
from django.db.models import Q, Count
from django.utils.functional import cached_property

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    founded_year = models.IntegerField()
    homeground = models.CharField(max_length=100)
    logo = models.CharField(max_length=255, null=True, blank=True)
    is_in_premier_league = models.BooleanField(default=True)

    # Optional fields for future use like social media handles, website, stadium capacity etc.
    website = models.URLField(blank=True, null=True)
    twitter_handle = models.CharField(max_length=50, blank=True, null=True)
    instagram_handle = models.CharField(max_length=50, blank=True, null=True)

    # actual fields for points, wins, etc., so the database doesn't have to calculate them on the fly.
    points = models.IntegerField(default=0)
    played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    
    ''' Logic for caluculating wins, losses, draws, Goals for a team
     Data cn be later used to calculate points and standings in the league table '''
    def get_stats(self):
        all_matches = Match.objects.filter(
            Q(home_team=self) | Q(away_team=self),
            match_status='FINISHED')
        
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
    def win_percentage(self):
        return self.stats['win_percentage']
    
    @property
    def form(self):
        return self.stats['form']

class Player(models.Model):
    class Position(models.TextChoices):
        GOALKEEPER = 'GK', 'Goalkeeper'
        DEFENDER = 'DEF', 'Defender'
        MIDFIELDER = 'MID', 'Midfielder'
        FORWARD = 'FWD', 'Forward'

    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    position = models.CharField(
        max_length=5,
        choices=Position.choices,
        default=Position.MIDFIELDER
        )
    date_of_birth = models.DateField(null=True, blank=True)
    assists = models.PositiveIntegerField(default=0) # For Future Use
    class Meta:
        # This prevents saving a player with the exact same name AND team twice
        unique_together = ('name', 'team')

    @property
    def age(self):
        ''' A property to calculate the age of the player based on their date of birth.
        This can be used to show player ages in the player profile and also for future features'''
        if not self.date_of_birth:
            return "N/A"
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        # Adjust if the birthday hasn't happened yet this year
        birthday_not_passed = (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        
        return age - (1 if birthday_not_passed else 0)
    
    @property
    def goals(self):
        # Counts events where this player was the scorer
        # We include GOAL and PENALTY
        return self.match_events.filter(
            event_type__in=[MatchEvent.EventType.GOAL, MatchEvent.EventType.PENALTY]
        ).count()

    @property
    def assists(self):
        # In a goal event, the 'related_player' is often the one who gave the assist
        # Or if you record an 'ASSIST' event type specifically:
        return self.match_events.filter(event_type=MatchEvent.EventType.ASSIST).count()
    
    @staticmethod
    def get_top_scorers(limit=10):
        # Get players annotated with their goal counts, then order by that count
        return Player.objects.annotate(
            goals_count=Count(
                'match_events', 
                filter=Q(match_events__event_type__in=[MatchEvent.EventType.GOAL, MatchEvent.EventType.PENALTY])
            )
        ).order_by('-goals_count')[:limit]

    @staticmethod
    def get_top_assists(limit=10):
        # Get players annotated with their assist counts, then order by that count
        return Player.objects.annotate(
            assists_count=Count(
                'match_events', 
                filter=Q(match_events__event_type=MatchEvent.EventType.ASSIST)
            )
        ).order_by('-assists_count')[:limit]

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
        LIVE = 'LIVE', 'LIVE'

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
        default=MatchStatus.UPCOMING
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
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, related_name='match_events', null=True, blank=True)

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
    minute = models.PositiveIntegerField(null=True, blank=True)  # Minute of the match when the event occurred

    class Meta:
        ordering = ['minute'] # Always sort events by time by default

    def __str__(self):
        player_name = self.player.name if self.player else "Unknown Player"
        return f"{self.get_event_type_display()} - {player_name} ({self.minute}')"
