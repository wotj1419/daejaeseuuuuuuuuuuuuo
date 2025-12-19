from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200)
    overview = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)

    poster_path = models.CharField(max_length=200, blank=True)
    backdrop_path = models.CharField(max_length=200, blank=True)

    vote_average = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0)

    genres = models.ManyToManyField(Genre, related_name='movies')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
