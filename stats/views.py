from datetime import timezone
from django.shortcuts import render, get_object_or_404
from . models import Team, Match, Player

# Create your views here.
def index(request):
    '''note: This view is for the homepage of the website. It will display the top teams, recent results and upcoming fixtures.'''
    all_teams = Team.objects.all()
    top_standings = sorted(all_teams, key=lambda t: (t.points, t.goal_difference), reverse=True)[:5]
    recent_results = Match.objects.filter(match_status='FINISHED').select_related('home_team', 'away_team').order_by('-date')[:5]
    upcoming_fixtures = Match.objects.filter(match_status='SCHEDULED').select_related('home_team', 'away_team').order_by('date')[:5]

    all_players = Player.objects.all()
    top_scorers = sorted(all_players, key=lambda p: p.goals, reverse=True)[:5]
    top_assists = sorted(all_players, key=lambda p: p.assists, reverse=True)[:5]

    # Clean Sheets Logic
    clean_sheets = sorted(all_teams, key=lambda t: getattr(t, 'clean_sheets', 0), reverse=True)[:5]

    return render(request, 'stats/home.html', {
        'standings': top_standings,
        'results': recent_results,
        'fixtures': upcoming_fixtures,
        'top_scorers': top_scorers,
        'top_assists': top_assists,
        'clean_sheets': clean_sheets
    })

def standings(request):
    teams = Team.objects.all()
    sorted_teams = sorted(teams, key=lambda t: (t.points, t.goal_difference), reverse=True)

    return render(request, 'stats/standings.html', {'teams': sorted_teams})

def resultsAndFixtures(request):
    ''' A view that dsiplay the recent and past match results'''

    results = Match.objects.filter(match_status='FINISHED').select_related('home_team', 'away_team').order_by('-date')[:10]
    fixtures = Match.objects.filter(match_status='SCHEDULED').select_related('home_team', 'away_team').order_by('date')[:10]

    context = {
        'results': results,
        'fixtures': fixtures
    }

    return render(request, 'stats/results_and_fixtures.html', context)

def match_detail(request, pk):
    ''' A view/function that finds and display a match or a 404 ERROR if match doesn't exist'''

    match = get_object_or_404(Match.objects.select_related('home_team', 'away_team'), pk=pk)

    return render(request, 'stats/match_detail.html', {'match': match})