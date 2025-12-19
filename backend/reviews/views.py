from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Review
from .serializers import ReviewSerializer
from movies.models import Movie
from django.shortcuts import get_object_or_404


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]  # 🔥 전부 허용

    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        return Review.objects.filter(movie_id=movie_id)

    def perform_create(self, serializer):
        movie = get_object_or_404(Movie, id=self.kwargs['movie_id'])
        serializer.save(movie=movie)  # 🔥 user 안 넣음

class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]  # 🔥 전부 허용

    def get_queryset(self):
        return Review.objects.all()

    # 🔥 수정 제한 없음
    def perform_update(self, serializer):
        serializer.save()

    # 🔥 삭제 제한 없음
    def perform_destroy(self, instance):
        instance.delete()
