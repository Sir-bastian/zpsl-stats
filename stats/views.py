from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. Welcome to ZPSL Stats Hub - Coming soon.")

def standings(request):
    return HttpResponse("ZPSL Standings - Coming Soon!")