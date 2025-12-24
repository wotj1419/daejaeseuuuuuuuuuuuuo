import logging
from math import radians, sin, cos, sqrt, atan2

import requests
from django.conf import settings
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BoardPost, BoardPostComment
from .serializers import BoardPostSerializer, BoardCommentSerializer

logger = logging.getLogger(__name__)


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


def _haversine(lat1, lon1, lat2, lon2):
    # Calculate the great-circle distance between two points
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return 6371.0 * c  # Earth radius in kilometers


class MapConfigView(APIView):
    """Returns public config needed by the client (e.g. Kakao Map key)."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # avoid auth errors when a stale token is sent

    def get(self, request):
        return Response({
            'kakao_api_key': settings.KAKAO_MAP_APP_KEY,
            'kakao_map_app_key': settings.KAKAO_MAP_APP_KEY,
        })


class NearbyBoardPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = float(request.query_params.get('radius', 20))

        if lat is None or lng is None:
            if user.latitude is None or user.longitude is None:
                return Response(
                    {'detail': '현재 위치가 설정되어 있지 않습니다.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            lat = user.latitude
            lng = user.longitude
        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response(
                {'detail': '위치 좌표가 유효하지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        following_ids = list(user.followings.values_list('pk', flat=True))
        queryset = BoardPost.objects.filter(
            board_type=BoardPost.BOARD_TYPE_FRIEND,
            latitude__isnull=False,
            longitude__isnull=False,
        ).filter(
            Q(author=user) | Q(author__in=following_ids) | Q(invited_users=user)
        ).distinct()
        nearby = []
        for post in queryset:
            distance = _haversine(lat, lng, post.latitude, post.longitude)
            if distance <= radius_km:
                post.distance_km = distance
                nearby.append((distance, post))
        nearby.sort(key=lambda item: item[0])
        serializer = BoardPostSerializer([item[1] for item in nearby], many=True)
        return Response({
            'results': serializer.data,
            'reference': {'latitude': lat, 'longitude': lng, 'radius_km': radius_km},
        })


class NearbyTheatersView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # public endpoint; ignore stale/invalid tokens

    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = int(request.query_params.get('radius', 20000))
        if lat is None or lng is None:
            return Response(
                {'detail': '좌표를 제공해주세요.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response(
                {'detail': '좌표가 유효하지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        kakao_key = settings.KAKAO_REST_API_KEY
        if not kakao_key:
            return Response(
                {'detail': '카카오 로컬 API 키가 설정되어 있지 않습니다.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
        headers = {
            'Authorization': f'KakaoAK {kakao_key}',
        }
        params = {
            'query': '영화관',
            'x': lng,
            'y': lat,
            'radius': radius,
            'size': 15,
            'category_group_code': 'AT4',
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            items = [
                {
                    'title': item.get('place_name'),
                    'address': item.get('road_address_name') or item.get('address_name'),
                    'telephone': item.get('telephone') or item.get('phone'),
                    'latitude': float(item.get('y')) if item.get('y') else None,
                    'longitude': float(item.get('x')) if item.get('x') else None,
                    'category': item.get('category_name'),
                    'place_url': item.get('place_url'),
                    'distance': float(item.get('distance')) if item.get('distance') else None,
                }
                for item in data.get('documents', [])
            ]
            return Response({'results': items})
        except requests.exceptions.RequestException as exc:
            logger.warning('Kakao local search failed: %s', exc)
            return Response(
                {'detail': '영화관 정보를 불러올 수 없습니다.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
