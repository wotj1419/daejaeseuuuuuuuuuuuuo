from django.conf import settings
from django.db import models
from common.models import TimeStampedModel


class BoardPost(TimeStampedModel):
    BOARD_TYPE_FREE = 'free'
    BOARD_TYPE_FRIEND = 'friend'
    BOARD_CHOICES = [
        (BOARD_TYPE_FREE, 'Free Board'),
        (BOARD_TYPE_FRIEND, 'Friend Board'),
    ]

    title = models.CharField(max_length=120)
    content = models.TextField()
    movie_title = models.CharField(max_length=255, blank=True, default='')
    board_type = models.CharField(
        max_length=10,
        choices=BOARD_CHOICES,
        default=BOARD_TYPE_FREE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='board_posts',
    )
    invited_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='board_invitations',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.board_type})'
