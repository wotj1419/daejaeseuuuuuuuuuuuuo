import logging

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import User
from .taste import update_user_taste_profile

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=User.favorite_movies.through)
def refresh_taste_on_favorite_change(sender, instance, action, **kwargs):
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    try:
        update_user_taste_profile(instance)
    except Exception as exc:  # pragma: no cover - non-critical path
        logger.exception('Failed to refresh taste profile for %s: %s', instance, exc)
