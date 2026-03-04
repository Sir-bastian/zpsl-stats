from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('standings/', views.standings, name='standings'),
    path('results-and-fixtures/', views.resultsAndFixtures, name='results_and_fixtures'),
    path('match/<int:pk>/', views.match_detail, name='match_detail')
]