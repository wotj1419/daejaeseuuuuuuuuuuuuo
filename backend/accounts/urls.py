from django.urls import path
from .views import (
    FavoriteMovieToggleView,
    ProfileView,
    MyFavoriteMoviesView,
    MyReviewsView,
    CheckFavoriteStatusView,
    UserFavoriteMoviesView,
)

urlpatterns = [
    path('favorites/<int:movie_id>/toggle/', FavoriteMovieToggleView.as_view()),
    path('favorites/<int:movie_id>/status/', CheckFavoriteStatusView.as_view()),
    path('my-movies/', MyFavoriteMoviesView.as_view()),
    path('users/<str:username>/favorites/', UserFavoriteMoviesView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('my-reviews/', MyReviewsView.as_view()),
]
