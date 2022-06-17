from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    tier = models.ForeignKey('Tier', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username


class Tier(models.Model):
    name = models.CharField(max_length=255)
    thumbnail_height = models.IntegerField()
    presence_of_original_file_link = models.BooleanField()
    ability_to_fetch_expiring_link = models.BooleanField()

    def __str__(self):
        return self.name
