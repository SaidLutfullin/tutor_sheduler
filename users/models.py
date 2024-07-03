from django.db import models
from django.contrib.auth.models import AbstractUser
from timezone_field import TimeZoneField


class User(AbstractUser):
    time_zone = TimeZoneField(default='UTC')
    is_tutor = models.BooleanField(default=True)