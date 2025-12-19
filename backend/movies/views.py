from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from django.conf import settings
import requests

from .models import Movie, Genre
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    MovieRecommendSerializer,
)


class MovieListAPIView(APIView):
    def get(self, request):
        movies = (
            Movie.objects
            .annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            )
            .order_by('-popularity')
        )
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)


class MovieDetailAPIView(APIView):
    def get_movie_from_tmdb(self, tmdb_id):
        tmdb_api_key = settings.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {
            'api_key': tmdb_api_key,
            'language': 'ko-KR',
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # 장르 처리
                genres = []
                if 'genres' in data:
                    for g in data['genres']:
                         genre, created = Genre.objects.get_or_create(
                             name=g['name']
                        )
                         genres.append(genre)

                # 영화 저장 (tmdb_id로 저장)
                movie, created = Movie.objects.get_or_create(
                    tmdb_id=data['id'],
                    defaults={
                        'title': data['title'],
                        'original_title': data.get('original_title', ''),
                        'overview': data.get('overview', ''),
                        'release_date': data.get('release_date') or None,
                        'poster_path': data.get('poster_path', ''),
                        'backdrop_path': data.get('backdrop_path', ''),
                        'vote_average': data.get('vote_average', 0),
                        'popularity': data.get('popularity', 0),
                    }
                )
                
                if created:
                     movie.genres.set(genres)
                
                return movie
        except Exception as e:
            print(f"Error fetching from TMDB: {e}")
            return None
        return None

    def get(self, request, movie_id):
        try:
            # 1. DB에서 tmdb_id로 찾기
            try:
                movie = Movie.objects.annotate(
                    avg_rating=Avg('reviews__rating'),
                    review_count=Count('reviews')
                ).get(tmdb_id=movie_id)
            except Movie.DoesNotExist:
                # 1.5 Legacy Fallback: 내부 ID로 한번 더 찾아보기 (기존 URL 호환성)
                try:
                    movie = Movie.objects.annotate(
                        avg_rating=Avg('reviews__rating'),
                        review_count=Count('reviews')
                    ).get(id=movie_id)
                except Movie.DoesNotExist:
                    # 2. DB에 없으면 TMDB에서 가져오기
                    movie = self.get_movie_from_tmdb(movie_id)
                    if not movie:
                         return Response({'error': '영화를 찾을 수 없습니다.'}, status=404)
                    
                    # Annotate 된 필드가 없으므로 수동으로 추가
                    movie.avg_rating = 0.0
                    movie.review_count = 0

            serializer = MovieDetailSerializer(movie)
            return Response(serializer.data)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)


class MovieRecommendAPIView(APIView):
    def get(self, request, movie_id):
        # movie_id는 이제 TMDB ID로 간주됨
        try:
            movie = Movie.objects.get(tmdb_id=movie_id)
        except Movie.DoesNotExist:
             return Response({'error': '영화를 찾을 수 없습니다.'}, status=404)

        genres = movie.genres.all()

        movies = (
            Movie.objects
            .filter(genres__in=genres)
            .exclude(tmdb_id=movie_id) # tmdb_id로 제외
            .distinct()
            .order_by('-vote_average', '-popularity')[:10]
        )

        serializer = MovieRecommendSerializer(movies, many=True)
        return Response(serializer.data)


class MovieSearchAPIView(APIView):
    """TMDB API를 사용하여 영화 검색"""
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({'results': [], 'message': '검색어를 입력해주세요.'}, status=400)
        
        api_key = settings.TMDB_API_KEY
        if not api_key:
            return Response({'error': 'TMDB API 키가 설정되지 않았습니다.'}, status=500)
        
        # TMDB 검색 API 호출
        tmdb_url = "https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': api_key,
            'query': query,
            'language': 'ko-KR',
            'page': 1
        }
        
        try:
            response = requests.get(tmdb_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 검색 결과를 정리하여 반환
            results = []
            for movie in data.get('results', [])[:20]:  # 최대 20개
                results.append({
                    'tmdb_id': movie.get('id'),
                    'title': movie.get('title'),
                    'original_title': movie.get('original_title'),
                    'overview': movie.get('overview', ''),
                    'release_date': movie.get('release_date'),
                    'poster_path': movie.get('poster_path', ''),
                    'backdrop_path': movie.get('backdrop_path', ''),
                    'vote_average': movie.get('vote_average', 0),
                    'vote_count': movie.get('vote_count', 0),
                    'popularity': movie.get('popularity', 0),
                })
            
            return Response({
                'results': results,
                'total_results': data.get('total_results', 0),
                'query': query
            })
            
        except requests.exceptions.RequestException as e:
            return Response({
                'error': 'TMDB API 호출 중 오류가 발생했습니다.',
                'detail': str(e)
            }, status=500)


class MovieTrailerAPIView(APIView):
    def get(self, request, movie_id):
        # movie_id는 이제 TMDB ID
        # DB에 영화가 없을 수도 있으니(상세페이지 갔다가 바로 예고편 로딩 시), 예고편은 TMDB API 바로 호출 가능
        # 하지만 기존 로직 유지해서 DB 조회 후 없으면 404
        
        # TMDB ID 자체를 그냥 써도 됨 (반드시 우리 DB에 있어야 하는 건 아님)
        tmdb_id = movie_id
        
        api_key = settings.TMDB_API_KEY
        if not api_key:
            return Response({"error": "TMDB API 키가 설정되지 않았습니다."}, status=500)

        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
        params = {
            "api_key": api_key,
            "language": "ko-KR",
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 404:
                 return Response({"trailer": None}, status=404)
                 
            response.raise_for_status()
            data = response.json()

            # YouTube Trailer만 필터링
            trailers = [
                video for video in data.get("results", [])
                if video.get("site") == "YouTube" and video.get("type") == "Trailer"
            ]

            if not trailers:
                return Response({"trailer": None})

            youtube_key = trailers[0]["key"]
            youtube_url = f"https://www.youtube.com/embed/{youtube_key}"

            return Response({
                "trailer": youtube_url
            })
        except requests.exceptions.RequestException as e:
            return Response({
                "error": "TMDB API 호출 중 오류가 발생했습니다.",
                "detail": str(e)
            }, status=500)
