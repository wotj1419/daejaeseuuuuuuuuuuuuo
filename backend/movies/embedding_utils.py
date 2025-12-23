import os
from functools import lru_cache
from typing import Iterable, List, Sequence

import numpy as np
from django.utils import timezone


def normalize_vector(vec: Sequence[float]) -> List[float]:
    """Return a unit-length vector. Empty/zero vectors stay zero-length."""
    arr = np.array(vec, dtype=np.float32)
    if arr.size == 0:
        return []
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr.tolist()
    return (arr / norm).tolist()


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def mean_embeddings(vectors: Iterable[Sequence[float]]) -> List[float]:
    items = [np.array(v, dtype=np.float32) for v in vectors if len(v)]
    if not items:
        return []
    stacked = np.vstack(items)
    mean_vec = stacked.mean(axis=0)
    return normalize_vector(mean_vec)


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the sentence-transformer model."""
    from sentence_transformers import SentenceTransformer

    model_name = os.getenv('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
    return SentenceTransformer(model_name)


def encode_text(text: str) -> List[float]:
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def build_movie_text(movie) -> str:
    """Concatenate useful textual fields for embedding."""
    genre_names = list(movie.genres.values_list('name', flat=True)) if hasattr(movie, 'genres') else []
    parts = [
        movie.title or '',
        getattr(movie, 'catchphrase', '') or '',
        movie.overview or '',
        ' '.join(genre_names),
    ]
    return '\n'.join([p for p in parts if p]).strip()


def ensure_movie_embedding(movie, force: bool = False) -> List[float]:
    """
    Compute and persist a normalized embedding for a movie if missing or forced.
    Returns the embedding list (may be empty on failure).
    """
    if movie.embedding and not force:
        return movie.embedding

    text = build_movie_text(movie)
    if not text:
        movie.embedding = []
        movie.embedding_updated_at = timezone.now()
        movie.save(update_fields=['embedding', 'embedding_updated_at'])
        return []

    embedding = encode_text(text)
    movie.embedding = embedding
    movie.embedding_updated_at = timezone.now()
    movie.save(update_fields=['embedding', 'embedding_updated_at'])
    return embedding
