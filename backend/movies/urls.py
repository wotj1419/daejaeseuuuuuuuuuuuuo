from django.urls import path
from .views import MovieRecommendAPIView

urlpatterns = [
    path('movies/<int:movie_id>/recommend/', MovieRecommendAPIView.as_view()),
]
