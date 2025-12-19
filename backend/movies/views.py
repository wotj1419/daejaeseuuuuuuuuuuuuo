from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from django.conf import settings
import requests

from .models import Movie
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
    def get(self, request, pk):
        movie = get_object_or_404(
            Movie.objects.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ),
            pk=pk
        )
        serializer = MovieDetailSerializer(movie)
        return Response(serializer.data)


class MovieRecommendAPIView(APIView):
    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)
        genres = movie.genres.all()

        movies = (
            Movie.objects
            .filter(genres__in=genres)
            .exclude(id=movie.id)
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
