from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

import shortuuid


STATUS_CHOICE = (
    ("w", "waiting"),
    ("s", "started"),
    ("f", "finished"),
)

def generate_short_uuid():
    return shortuuid.ShortUUID().random(length=10)


class Race(models.Model):
    id = models.CharField(max_length=10, primary_key=True, default=generate_short_uuid, editable=False, unique=True)
    creator = models.ForeignKey(User, related_name="created_races", on_delete=models.SET_NULL, null=True)

    status = models.CharField(choices=STATUS_CHOICE, max_length=1, default="w")
    quote = models.ForeignKey("quotes_interface.Quotes", on_delete=models.SET_NULL, related_name="races", null=True)

    participants = models.ManyToManyField(User, related_name="races", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class RaceStatistics(models.Model):
    time_racing = models.DurationField(blank=True, null=True)

    player = models.ForeignKey(User, related_name="races_statistics", blank=True, on_delete=models.SET_NULL, null=True)
    
    race = models.ForeignKey(Race, on_delete=models.SET_NULL, related_name="statistics", null=True)

    finished = models.BooleanField(default=False)
    # progress = models.DecimalField(max_digits=4, decimal_places=3, validators=[
    #         MaxValueValidator(1),
    #         MinValueValidator(0)
    #     ], default=0)

    # characters_typed = models.PositiveIntegerField()
    
