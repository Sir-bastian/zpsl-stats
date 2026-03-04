from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from . models import Team, Match

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello, world. Welcome to ZPSL Stats Hub - Coming soon.</h1>")

def standings(request):
    teams = Team.objects.all()
    sorted_teams = sorted(teams, key=lambda t: (t.points, t.goal_difference), reverse=True)

    return render(request, 'stats/standings.html', {'teams': sorted_teams})

def resultsAndFixtures(request):
    ''' A view that dsiplay the recent and past match results'''

    results = Match.objects.filter(match_status='Completed').select_related('home_team', 'away_team').order_by('-date')[:10]
    fixtures = Match.objects.filter(match_status='Scheduled').select_related('home_team', 'away_team').order_by('date')[:10]

    context = {
        'results': results,
        'fixtures': fixtures
    }

    return render(request, 'stats/results_and_fixtures.html', context)

def match_detail(request, pk):
    ''' A view/function that finds and display a match or a 404 ERROR if match doesn't exist'''

    match = get_object_or_404(Match.objects.select_related('home_team', 'away_team'), pk=pk)

    return render(request, 'stats/match_detail.html', {'match': match})