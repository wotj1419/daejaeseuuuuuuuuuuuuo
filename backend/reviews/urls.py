from django.urls import path
from .views import ReviewListCreateAPIView, ReviewDetailAPIView

urlpatterns = [
    path('movies/<int:movie_id>/reviews/', ReviewListCreateAPIView.as_view()),
    path('reviews/<int:pk>/', ReviewDetailAPIView.as_view()),
]
