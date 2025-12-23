from django.urls import path
from .views import (
    FavoriteMovieToggleView,
    ProfileView,
    MyProfileSummaryView,
    MyFavoriteMoviesView,
    MyFollowingsListView,
    MyFollowersListView,
    MyReviewsView,
    UserListView,
    FollowToggleView,
    CheckFavoriteStatusView,
    UserFavoriteMoviesView,
    MyTasteView,
    SimilarUsersByTasteView,
    MyLocationView,
)

urlpatterns = [
    path('favorites/<int:movie_id>/toggle/', FavoriteMovieToggleView.as_view()),
    path('favorites/<int:movie_id>/status/', CheckFavoriteStatusView.as_view()),
    path('my-movies/', MyFavoriteMoviesView.as_view()),
    path('users/<str:username>/favorites/', UserFavoriteMoviesView.as_view()),
    # New taste + similarity endpoints
    path('me/taste/', MyTasteView.as_view()),
    path('me/similar-users/', SimilarUsersByTasteView.as_view()),
    # Backwards compatibility for older route
    path('favorites/similar-users/', SimilarUsersByTasteView.as_view()),
    path('my-location/', MyLocationView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('profile/summary/', MyProfileSummaryView.as_view()),
    path('my-reviews/', MyReviewsView.as_view()),
    path('followings/', MyFollowingsListView.as_view()),
    path('followers/', MyFollowersListView.as_view()),
    path('users/', UserListView.as_view()),
    path('follow/<str:username>/toggle/', FollowToggleView.as_view()),
]
