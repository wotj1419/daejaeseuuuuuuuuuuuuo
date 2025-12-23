from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models import TimeStampedModel


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
    profile_image = models.TextField(blank=True, default='')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


class TasteProfile(TimeStampedModel):
    """Cached user taste embedding + summary derived from liked movies."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='taste_profile')
    embedding = models.JSONField(default=list, blank=True)
    liked_movies_count = models.IntegerField(default=0)
    top_genres = models.JSONField(default=list, blank=True)  # [{'name': str, 'score': float}]
    summary = models.TextField(blank=True, default='')

    def __str__(self):
        return f"TasteProfile<{self.user.username}>"
