import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movie
from .embedding_utils import ensure_movie_embedding

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Movie)
def auto_generate_movie_embedding(sender, instance, created, **kwargs):
    """자동으로 새 영화의 임베딩 생성"""
    if created and not instance.embedding:
        try:
            ensure_movie_embedding(instance)
            logger.info(f"Auto-generated embedding for movie: {instance.title}")
        except Exception as e:
            logger.warning(f"Failed to auto-generate embedding for {instance.title}: {e}")
