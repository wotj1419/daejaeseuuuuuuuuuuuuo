from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Review
from .serializers import ReviewSerializer
from movies.models import Movie
from django.shortcuts import get_object_or_404


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Frontend passes TMDB ID as movie_id in URL
        movie_id = self.kwargs['movie_id']
        movie = get_object_or_404(Movie, tmdb_id=movie_id)
        return Review.objects.filter(movie=movie)

    def perform_create(self, serializer):
        movie_id = self.kwargs['movie_id']
        movie = get_object_or_404(Movie, tmdb_id=movie_id)
        serializer.save(user=self.request.user, movie=movie)

class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.all()

    def perform_update(self, serializer):
        if self.get_object().user != self.request.user:
            raise PermissionDenied("수정 권한이 없습니다.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("삭제 권한이 없습니다.")
        instance.delete()
