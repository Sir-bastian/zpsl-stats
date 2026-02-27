from django.shortcuts import render
from django.http import HttpResponse
from . models import Team

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. Welcome to ZPSL Stats Hub - Coming soon.")

def standings(request):
    team = Team.objects.all()

    return HttpResponse("ZPSL Standings - Coming Soon!")