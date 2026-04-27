from datetime import timezone
from django.shortcuts import render, get_object_or_404
from . models import Team, Match, Player
from django.db.models import Q

# Create your views here.
def index(request):
    '''note: This view is for the homepage of the website. It will display the top teams, recent results and upcoming fixtures.'''
    all_teams = Team.objects.all()
    top_standings = sorted(all_teams, key=lambda t: (t.points, t.goal_difference), reverse=True)[:5]
    recent_results = Match.objects.filter(match_status='FINISHED').select_related('home_team', 'away_team').order_by('-date')[:5]
    upcoming_fixtures = Match.objects.filter(match_status='SCHEDULED').select_related('home_team', 'away_team').order_by('date')[:5]

    top_scorers = Player.get_top_scorers()[:10]
    top_assists = Player.get_top_assists()[:10]

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
    teams = Team.objects.filter(is_in_premier_league=True).order_by(
        '-played'
        '-points', 
        '-goal_difference', 
        '-goals_for'
    )
    return render(request, 'stats/standings.html', {'teams': teams})

def resultsAndFixtures(request):
    ''' A view that dsiplay the recent and past match results'''

    results = Match.objects.filter(match_status='FINISHED').select_related('home_team', 'away_team').order_by('-date')[:10]
    fixtures = Match.objects.filter(match_status='SCHEDULED').select_related('home_team', 'away_team').order_by('date')[:10]

    context = {
        'results': results,
        'fixtures': fixtures
    }

    return render(request, 'stats/results_and_fixtures.html', context)

def match_detail(request, match_id):
    ''' A view/function that finds and display a match or a 404 ERROR if match doesn't exist'''
    # We fetch the match and "prefetch" events to avoid the N+1 query problem when we later access match.match_events in the template.
    match = get_object_or_404(
        Match.objects.select_related('home_team', 'away_team').prefetch_related('events__player'),
        id=match_id
    )

    # Seperate Events by team for the template
    home_events = match.events.filter(player__team=match.home_team).order_by('minute')
    away_events = match.events.filter(player__team=match.away_team).order_by('minute')

    context = {
        'match': match,
        'home_events': home_events,
        'away_events': away_events
    }

    return render(request, 'stats/match_detail.html', context)