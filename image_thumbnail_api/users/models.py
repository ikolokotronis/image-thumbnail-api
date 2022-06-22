from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    """
    Custom User Model
    """
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    tier = models.ForeignKey('Tier', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username


class Tier(models.Model):
    """
    This model is used to store the different tiers that a user can have.
    """
    name = models.CharField(max_length=255)
    thumbnail_height = models.IntegerField(null=True, blank=True)  # can be null for built-in tiers
    presence_of_original_file_link = models.BooleanField()
    ability_to_fetch_expiring_link = models.BooleanField()

    def __str__(self):
        return self.name


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Create a token for each user when they are created/registered
    """
    if created:
        Token.objects.create(user=instance)
