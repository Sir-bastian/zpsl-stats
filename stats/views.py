from django.shortcuts import render
from django.http import HttpResponse
from . models import Team

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. Welcome to ZPSL Stats Hub - Coming soon.")

def standings(request):
    teams = Team.objects.all()
    sorted_teams = sorted(teams, key=lambda t: (t.points, t.goal_difference), reverse=True)

    return render(request, 'stats/standings.html', {'teams': sorted_teams})