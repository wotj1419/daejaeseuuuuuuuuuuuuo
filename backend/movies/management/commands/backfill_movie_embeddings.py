from django.core.management.base import BaseCommand
from django.db import transaction

from movies.embedding_utils import ensure_movie_embedding
from movies.models import Movie


class Command(BaseCommand):
    help = "Compute and store embeddings for movies (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Recompute even if embedding exists.')
        parser.add_argument('--limit', type=int, help='Limit number of movies processed.')

    def handle(self, *args, **options):
        force = options.get('force', False)
        limit = options.get('limit')

        qs = Movie.objects.all().order_by('id')
        if limit:
            qs = qs[:limit]

        processed = 0
        for movie in qs:
            if movie.embedding and not force:
                continue
            with transaction.atomic():
                ensure_movie_embedding(movie, force=force)
            processed += 1
            if processed % 20 == 0:
                self.stdout.write(f"Processed {processed} movies...")

        self.stdout.write(self.style.SUCCESS(f"Embedding backfill complete. Updated {processed} movies."))
