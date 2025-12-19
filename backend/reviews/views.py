from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer
from movies.models import Movie
from django.shortcuts import get_object_or_404

class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        return Review.objects.filter(movie_id=movie_id)

    def perform_create(self, serializer):
        movie = get_object_or_404(Movie, id=self.kwargs['movie_id'])
        serializer.save(
            user=self.request.user,
            movie=movie
        )


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.all()

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.user:
            raise PermissionError("수정 권한 없음")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user:
            raise PermissionError("삭제 권한 없음")
        instance.delete()
