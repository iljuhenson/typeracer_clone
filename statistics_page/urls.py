from django.urls import path
from . import views


urlpatterns = [
    path('stats/', views.currentUserStatsView, name="race_list"),
]