from django.utils import timezone
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

def get_standings_data():
    return Team.objects.filter(is_in_premier_league=True).order_by(
        '-points', 
        '-goal_difference', 
        '-goals_for'
    )

def standings(request):
    teams = get_standings_data()
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
        Match.objects.select_related('home_team', 'away_team')
                     .prefetch_related('events__player'),
        id=match_id
    )

    # Initialize variables to avoid UnboundLocalError
    home_events, away_events = [], []
    
    # Use the object status, not new queries
    is_active = match.match_status in [Match.MatchStatus.Completed, Match.MatchStatus.LIVE]
    
    if is_active:
        # Filtering in Python is faster since you already prefetched the events
        home_events = [e for e in match.events.all() if e.player.team == match.home_team]
        away_events = [e for e in match.events.all() if e.player.team == match.away_team]

    context = {
        'match': match,
        'home_events': home_events,
        'away_events': away_events,
        'is_finished': (match.match_status == Match.MatchStatus.Completed),
        'is_live': (match.match_status == Match.MatchStatus.LIVE),
    }

    return render(request, 'stats/match_detail.html', context)

def team_detail(request, team_id):
    ''' A view/function that finds and display a team or a 404 ERROR if team doesn't exist'''
    queryset = Team.objects.prefetch_related('player_set')
    team = get_object_or_404(queryset, id=team_id)

    # The most recent results
    recent_results = Match.objects.filter(
        Q(home_team = team) | Q(away_team=team),
        match_status = 'FINISHED'
    ).select_related('home_team', 'away_team').order_by('-date', '-time') #[:5]

    # Next Fixture ( The very next ONE fixture, not all upcoming fixtures)
    next_fixture = Match.objects.filter(
        Q(home_team=team) | Q(away_team=team),
        match_status = 'SCHEDULED',
        date__gte=timezone.now().date()
    ).select_related('home_team', 'away_team').order_by('date').first()

    # Players
    players = team.player_set.all().order_by('position')

    all_teams = list(get_standings_data()) # Fetch once, convert to list for indexing
    
    # Find rank (1-based)
    team_rank = next((i + 1 for i, t in enumerate(all_teams) if t.id == team.id), None)

    relative_standings = []
    start_rank = 1

    if team_rank:
        idx = team_rank - 1
        count = len(all_teams)
        
        # Calculate window (showing 7 teams total)
        start = max(0, idx - 3)
        end = start + 7
        
        if end > count:
            end = count
            start = max(0, end - 7)
            
        relative_standings = all_teams[start:end]
        start_rank = start + 1

    context = {
        'team': team,
        'recent_results': recent_results,
        'next_fixture': next_fixture,
        'players': players,
        'team_rank': team_rank,
        'relative_standings': relative_standings,
        'start_rank': start_rank
    }

    return render(request, 'stats/team_detail.html', context)