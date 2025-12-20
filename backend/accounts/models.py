from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    favorite_movies = models.ManyToManyField(
        'movies.Movie',
        related_name='favorited_by',
        blank=True
    )
