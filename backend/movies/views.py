from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count

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
