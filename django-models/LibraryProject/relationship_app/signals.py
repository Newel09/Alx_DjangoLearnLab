"""
Django signals for relationship_app

This module defines signal handlers for automatic model operations,
such as creating a UserProfile when a new User is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_userprofile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a UserProfile when a new User is created.
    This ensures every user has an associated profile with a default role of 'member'.
    """
    if created:
        UserProfile.objects.create(user=instance, role='member')


@receiver(post_save, sender=User)
def save_userprofile(sender, instance, **kwargs):
    """
    Signal handler to save UserProfile whenever User is saved.
    This ensures the UserProfile is updated if the user object changes.
    """
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
