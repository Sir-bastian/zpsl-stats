from django.db import models

# Create your models here.
class Teams(models.Model):
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
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    position = models.CharField(max_length=50)
    age = models.IntegerField()

    def __str__(self):
        return (
            f"Player: {self.name}, Team: {self.team.name}, "
            f"Position: {self.position}, Age: {self.age}"
        )

class Standings(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, null=True, blank=True)
    games_played = models.IntegerField()
    points = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    draws = models.IntegerField()
    goals_for = models.IntegerField()
    goals_against = models.IntegerField()

    def __str__(self):
        return (
            f"Team: {self.team.name}, Games Played: {self.games_played}, "
            f"Points: {self.points}, Wins: {self.wins}, Losses: {self.losses}, "
            f"Draws: {self.draws}, Goals For: {self.goals_for}, "
            f"Goals Against: {self.goals_against}"
        )

class TopScorer(models.Model):
    player_name = models.CharField(max_length=100)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    goals_scored = models.IntegerField()
    games_played = models.IntegerField()

    def __str__(self):
        return (
            f"Player: {self.player_name}, Team: {self.team.name}, "
            f"Goals Scored: {self.goals_scored}, Games Played: {self.games_played}"
        )