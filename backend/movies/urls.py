from django.urls import path
from .views import (
    MovieListAPIView,
    MovieDetailAPIView,
    MovieRecommendAPIView,
    MovieSearchAPIView,
)

urlpatterns = [
    path('movies/', MovieListAPIView.as_view()),
    path('movies/<int:pk>/', MovieDetailAPIView.as_view()),
    path('movies/<int:movie_id>/recommend/', MovieRecommendAPIView.as_view()),
    path('movies/search/', MovieSearchAPIView.as_view()),
]
