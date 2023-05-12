# Generated by Django 4.2 on 2023-04-30 19:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('race_handler', '0004_alter_race_participants_alter_race_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='race',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='races', to=settings.AUTH_USER_MODEL),
        ),
    ]