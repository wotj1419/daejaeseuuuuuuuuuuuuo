from django.urls import path
from .views import (
    FreeBoardListCreateView,
    FreeBoardDetailView,
    BoardCommentListCreateView,
    BoardCommentDetailView,
    BoardPostRecommendView,
    FriendBoardListCreateView,
    MapConfigView,
    NearbyBoardPostsView,
    NearbyTheatersView,
)
from .views_showtimes_stub import ShowtimesView

urlpatterns = [
    path('free/<int:pk>/', FreeBoardDetailView.as_view()),
    path('free/<int:pk>/recommend/', BoardPostRecommendView.as_view()),
    path('free/<int:post_id>/comments/', BoardCommentListCreateView.as_view()),
    path('free/comments/<int:pk>/', BoardCommentDetailView.as_view()),
    path('free/', FreeBoardListCreateView.as_view()),
    path('friends/', FriendBoardListCreateView.as_view()),
    path('map-config/', MapConfigView.as_view()),
    path('nearby/', NearbyBoardPostsView.as_view()),
    path('theaters/', NearbyTheatersView.as_view()),
    path('theaters/showtimes/', ShowtimesView.as_view()),
]
