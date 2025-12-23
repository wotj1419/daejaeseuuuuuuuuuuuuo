from typing import List, Tuple

from django.db import transaction
from django.db.models import Count
from .models import TasteProfile, User
from movies.embedding_utils import ensure_movie_embedding, mean_embeddings

MIN_LIKED_FOR_TASTE = 5


def _top_genres_for_user(user: User) -> List[dict]:
    rows = (
        user.favorite_movies.values('genres__name')
        .annotate(c=Count('genres__name'))
        .order_by('-c')
    )
    total = sum(r['c'] for r in rows if r.get('genres__name'))
    top = []
    for row in rows:
        name = row.get('genres__name')
        if not name:
            continue
        score = round(row['c'] / total, 3) if total else 0
        top.append({'name': name, 'score': score})
        if len(top) >= 5:
            break
    return top


def _summary_from_signals(user: User, top_genres: List[dict], sample_titles: List[str], liked_count: int) -> str:
    if liked_count < MIN_LIKED_FOR_TASTE:
        return '좋아요한 영화가 5개 미만이라 취향을 요약하지 않았어요.'

    genre_text = ', '.join([g['name'] for g in top_genres[:3]]) if top_genres else '다양한 장르'
    title_text = ', '.join(sample_titles[:3]) if sample_titles else '대표작 정보 없음'
    return f"{user.username}님은 {genre_text} 장르를 즐겨보고, {title_text} 등을 좋아합니다. (좋아요 {liked_count}개 기준)"


@transaction.atomic
def update_user_taste_profile(user: User, force: bool = False) -> TasteProfile:
    """Recompute and persist a user's taste profile."""
    liked_qs = user.favorite_movies.all().prefetch_related('genres')
    liked_count = liked_qs.count()
    profile, _ = TasteProfile.objects.get_or_create(user=user)

    # Early exit when not enough data
    if liked_count < MIN_LIKED_FOR_TASTE:
        profile.embedding = []
        profile.top_genres = []
        profile.liked_movies_count = liked_count
        profile.summary = _summary_from_signals(user, [], [], liked_count)
        profile.save(update_fields=['embedding', 'top_genres', 'liked_movies_count', 'summary', 'updated_at'])
        return profile

    embeddings = []
    for movie in liked_qs:
        if not movie.embedding or force:
            ensure_movie_embedding(movie, force=force)
        if movie.embedding:
            embeddings.append(movie.embedding)

    top_genres = _top_genres_for_user(user)
    sample_titles = list(liked_qs.values_list('title', flat=True)[:5])

    if not embeddings:
        profile.embedding = []
        profile.top_genres = top_genres
        profile.liked_movies_count = liked_count
        profile.summary = '선호 영화 임베딩이 준비되지 않았어요.'
        profile.save(update_fields=['embedding', 'top_genres', 'liked_movies_count', 'summary', 'updated_at'])
        return profile

    embedding = mean_embeddings(embeddings)
    profile.embedding = embedding
    profile.top_genres = top_genres
    profile.liked_movies_count = liked_count
    profile.summary = _summary_from_signals(user, top_genres, sample_titles, liked_count)
    profile.save(update_fields=['embedding', 'top_genres', 'liked_movies_count', 'summary', 'updated_at'])
    return profile


def ensure_taste_profile(user: User) -> TasteProfile:
    return update_user_taste_profile(user, force=False)
