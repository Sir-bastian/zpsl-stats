from django.db import models

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    founded_year = models.IntegerField()
    homeground = models.CharField(max_length=100)

    def __str__(self):
        return (
            f"Team: {self.name}, City: {self.city}, "
            f"Founded: {self.founded_year}, Homeground: {self.homeground}"
        )

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