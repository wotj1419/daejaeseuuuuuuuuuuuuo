from django.core.management.base import BaseCommand
from movies.models import Movie, Genre
from django.conf import settings
import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3"

class Command(BaseCommand):
    help = "TMDB API로 영화 데이터 로드"

    def handle(self, *args, **options):
        api_key = settings.TMDB_API_KEY

        # 1️⃣ 장르 먼저 수집
        genre_url = f"{TMDB_BASE_URL}/genre/movie/list"
        genre_res = requests.get(genre_url, params={"api_key": api_key, "language": "ko"})
        genre_data = genre_res.json()["genres"]

        genre_map = {}
        for g in genre_data:
            genre, _ = Genre.objects.get_or_create(name=g["name"])
            genre_map[g["id"]] = genre

        # 2️⃣ 인기 영화 수집 (여러 페이지)
        for page in range(1, 4):  # 약 60개
            movie_url = f"{TMDB_BASE_URL}/movie/popular"
            res = requests.get(
                movie_url,
                params={
                    "api_key": api_key,
                    "language": "ko",
                    "page": page
                }
            )

            for m in res.json()["results"]:
                movie, created = Movie.objects.get_or_create(
                    tmdb_id=m["id"],
                    defaults={
                        "title": m["title"],
                        "original_title": m["original_title"],
                        "overview": m["overview"],
                        "release_date": m["release_date"] or None,
                        "poster_path": m["poster_path"] or "",
                        "backdrop_path": m["backdrop_path"] or "",
                        "vote_average": m["vote_average"],
                        "vote_count": m["vote_count"],
                        "popularity": m["popularity"],
                    }
                )

                if created:
                    for gid in m["genre_ids"]:
                        movie.genres.add(genre_map[gid])

        self.stdout.write(self.style.SUCCESS("🎬 영화 데이터 로드 완료"))
