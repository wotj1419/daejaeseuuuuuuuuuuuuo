from django.db import models
from django.conf import settings
from movies.models import Movie
from common.models import TimeStampedModel

User = settings.AUTH_USER_MODEL


class Review(TimeStampedModel):
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,   # 🔥 핵심
        null=True,                   # 🔥 익명 허용
        blank=True,
        related_name='reviews'
    )
    content = models.TextField()
    rating = models.IntegerField()  # 1~5

    class Meta:
        # 🔥 익명 리뷰 허용하므로 제거
        # unique_together = ('movie', 'user')
        pass

    def __str__(self):
        if self.user:
            return f"{self.movie.title} - {self.user}"
        return f"{self.movie.title} - 익명"
