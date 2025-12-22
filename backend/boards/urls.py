from django.urls import path
from .views import FreeBoardListCreateView, FriendBoardListCreateView

urlpatterns = [
    path('free/', FreeBoardListCreateView.as_view()),
    path('friends/', FriendBoardListCreateView.as_view()),
]
