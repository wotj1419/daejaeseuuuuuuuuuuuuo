from django.db import models
from django.conf import settings
from movies.models import Movie

User = settings.AUTH_USER_MODEL


class Review(models.Model):
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='reviews'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    content = models.TextField()
    rating = models.IntegerField()  # 1~5
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('movie', 'user')  # 한 영화에 리뷰 1개

    def __str__(self):
        return f"{self.movie.title} - {self.user}"
