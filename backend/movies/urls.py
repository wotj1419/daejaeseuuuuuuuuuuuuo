from django.urls import path
from .views import (
    MovieListAPIView,
    MovieDetailAPIView,
    MovieRecommendAPIView,
    MovieSearchAPIView,
    MovieTrailerAPIView,
    MovieCreditsAPIView,
    PersonDetailAPIView,
    GenreListAPIView,
)
from .views_ai import MovieAIRecommendAPIView

urlpatterns = [
    path('movies/', MovieListAPIView.as_view()),
    path('genres/', GenreListAPIView.as_view()),
    path('movies/<int:movie_id>/', MovieDetailAPIView.as_view()),
    path('movies/<int:movie_id>/recommend/', MovieRecommendAPIView.as_view()),
    path('movies/search/', MovieSearchAPIView.as_view()),
    path('movies/<int:movie_id>/trailer/', MovieTrailerAPIView.as_view()),
    path('movies/<int:movie_id>/credits/', MovieCreditsAPIView.as_view()),
    path('person/<int:person_id>/', PersonDetailAPIView.as_view()),
    path('movies/ai-recommend/', MovieAIRecommendAPIView.as_view()),
]
