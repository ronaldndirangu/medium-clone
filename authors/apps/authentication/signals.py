from django.db.models.signals import post_save
from django.dispatch import receiver

#my local imports
from authors.apps.profiles.models import Profile
from .models import User


@receiver(post_save, sender=User)
def create_related_profile(sender, instance, created, *args, **kwargs):
    """
    This is the signal to create a profile object 
    every time a user is created
    """

    if instance and created:
        instance.profile = Profile.objects.create(user=instance)
