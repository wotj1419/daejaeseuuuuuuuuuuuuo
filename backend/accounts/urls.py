from django.urls import path
from .views import (
    FavoriteMovieToggleView,
    MyFavoriteMoviesView,
    MyReviewsView,
    CheckFavoriteStatusView,
)

urlpatterns = [
    path('favorites/<int:movie_id>/toggle/', FavoriteMovieToggleView.as_view()),
    path('favorites/<int:movie_id>/status/', CheckFavoriteStatusView.as_view()),
    path('my-movies/', MyFavoriteMoviesView.as_view()),
    path('my-reviews/', MyReviewsView.as_view()),
]
