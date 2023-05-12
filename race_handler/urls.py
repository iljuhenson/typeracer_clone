from django.urls import path
from . import views


urlpatterns = [
    path('races/available/', views.race_list, name="race_list"),
    path('races/race/create/', views.create_race, name="race_create")
]
