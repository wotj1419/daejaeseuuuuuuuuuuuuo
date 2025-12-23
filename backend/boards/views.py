from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BoardPost, BoardPostComment
from .serializers import BoardPostSerializer, BoardCommentSerializer


class FreeBoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return BoardPost.objects.filter(board_type=BoardPost.BOARD_TYPE_FREE)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, board_type=BoardPost.BOARD_TYPE_FREE)


class FreeBoardDetailView(generics.RetrieveAPIView):
    serializer_class = BoardPostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BoardPost.objects.filter(board_type=BoardPost.BOARD_TYPE_FREE)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        BoardPost.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db(fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BoardCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return BoardPostComment.objects.filter(post__pk=post_id).order_by('created_at')

    def perform_create(self, serializer):
        post = get_object_or_404(BoardPost, pk=self.kwargs['post_id'], board_type=BoardPost.BOARD_TYPE_FREE)
        serializer.save(post=post, author=self.request.user)
        BoardPost.objects.filter(pk=post.pk).update(comment_count=F('comment_count') + 1)


class BoardCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BoardPostComment.objects.all()

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise PermissionDenied('댓글 작성자만 수정할 수 있습니다.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('댓글 작성자만 삭제할 수 있습니다.')
        BoardPost.objects.filter(pk=instance.post.pk, comment_count__gt=0).update(
            comment_count=F('comment_count') - 1
        )
        instance.delete()


class BoardPostRecommendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(BoardPost, pk=pk, board_type=BoardPost.BOARD_TYPE_FREE)
        BoardPost.objects.filter(pk=post.pk).update(recommendation_count=F('recommendation_count') + 1)
        post.refresh_from_db(fields=['recommendation_count'])
        serializer = BoardPostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
