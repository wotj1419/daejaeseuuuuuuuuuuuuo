from django.urls import path
from .views import (
    MovieListAPIView,
    MovieDetailAPIView,
    MovieRecommendAPIView,
    MovieSearchAPIView,
    MovieSearchAPIView,
    MovieTrailerAPIView,
)
from .views_ai import MovieAIRecommendAPIView

urlpatterns = [
    path('movies/', MovieListAPIView.as_view()),
    path('movies/<int:movie_id>/', MovieDetailAPIView.as_view()),
    path('movies/<int:movie_id>/recommend/', MovieRecommendAPIView.as_view()),
    path('movies/search/', MovieSearchAPIView.as_view()),
    path('movies/<int:movie_id>/trailer/', MovieTrailerAPIView.as_view()),
    path('movies/ai-recommend/', MovieAIRecommendAPIView.as_view()),
]
