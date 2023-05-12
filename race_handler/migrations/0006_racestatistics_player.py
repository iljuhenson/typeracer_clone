# Generated by Django 4.2 on 2023-05-03 18:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('race_handler', '0005_alter_race_participants'),
    ]

    operations = [
        migrations.AddField(
            model_name='racestatistics',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='races_statistics', to=settings.AUTH_USER_MODEL),
        ),
    ]
