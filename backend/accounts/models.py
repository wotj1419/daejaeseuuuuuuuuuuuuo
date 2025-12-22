from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    favorite_movies = models.ManyToManyField(
        'movies.Movie',
        related_name='favorited_by',
        blank=True
    )
    followings = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )
    bio = models.TextField(blank=True, default='')
    favorite_movie_name = models.CharField(max_length=255, blank=True, default='')
