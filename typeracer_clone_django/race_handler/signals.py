from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from models import ParticipantSettings


@receiver(post_save, sender=User)
def create_favorites(sender, instance, created, **kwargs):
    if created:
        ParticipantSettings.objects.get_or_create(user=instance)
