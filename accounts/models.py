from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=[
        ('read', 'Read'),
        ('write', 'Write'),
        ('admin', 'Admin')
    ], default='read')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
