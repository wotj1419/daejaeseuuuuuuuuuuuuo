from rest_framework import generics, permissions
from django.db.models import Q
from .models import BoardPost
from .serializers import BoardPostSerializer


class FreeBoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return BoardPost.objects.filter(board_type=BoardPost.BOARD_TYPE_FREE)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, board_type=BoardPost.BOARD_TYPE_FREE)


class FriendBoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return BoardPost.objects.filter(
            Q(board_type=BoardPost.BOARD_TYPE_FRIEND),
            Q(author=user) | Q(invited_users=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, board_type=BoardPost.BOARD_TYPE_FRIEND)
