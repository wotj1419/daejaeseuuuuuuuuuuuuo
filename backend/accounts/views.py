import logging
from typing import List

import requests
from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .taste import ensure_taste_profile, update_user_taste_profile, MIN_LIKED_FOR_TASTE
from movies.embedding_utils import cosine_similarity
from movies.models import Genre, Movie
from movies.serializers import MovieListSerializer
from reviews.models import Review
from reviews.serializers import ReviewSerializer

logger = logging.getLogger(__name__)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'bio', 'favorite_movie_name', 'profile_image')
        read_only_fields = ('username',)


class UserSummarySerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'bio',
            'favorite_movie_name',
            'profile_image',
            'follower_count',
            'following_count',
        )
        read_only_fields = ('username',)

    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.followings.count()


class FollowSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'bio', 'favorite_movie_name', 'profile_image', 'is_following')

    def get_is_following(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return user.followings.filter(pk=obj.pk).exists()
        return False


class UserListSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'bio',
            'favorite_movie_name',
            'profile_image',
            'is_following',
            'is_followed_by',
        )

    def get_is_following(self, obj):
        following_ids = self.context.get('following_ids')
        if following_ids is not None:
            return obj.pk in following_ids

        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if user and user.is_authenticated:
            return user.followings.filter(pk=obj.pk).exists()
        return False

    def get_is_followed_by(self, obj):
        follower_ids = self.context.get('follower_ids')
        if follower_ids is not None:
            return obj.pk in follower_ids

        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if user and user.is_authenticated:
            return obj.followings.filter(pk=user.pk).exists()
        return False


class FavoriteMovieToggleView(APIView):
    """좋아요 추가/취소"""

    permission_classes = [permissions.IsAuthenticated]

    def get_movie_from_tmdb(self, tmdb_id):
        api_key = settings.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {'api_key': api_key, 'language': 'ko-KR'}
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            genres = []
            if 'genres' in data:
                for g in data['genres']:
                    genre, _ = Genre.objects.get_or_create(name=g['name'])
                    genres.append(genre)

            movie, created = Movie.objects.get_or_create(
                tmdb_id=data['id'],
                defaults={
                    'title': data['title'],
                    'original_title': data.get('original_title', ''),
                    'overview': data.get('overview', ''),
                    'release_date': data.get('release_date') or None,
                    'poster_path': data.get('poster_path', ''),
                    'backdrop_path': data.get('backdrop_path', ''),
                    'vote_average': data.get('vote_average', 0),
                    'popularity': data.get('popularity', 0),
                },
            )

            if created and genres:
                movie.genres.set(genres)

            return movie
        except Exception as exc:
            logger.exception("TMDB fetch failed for %s: %s", tmdb_id, exc)
            return None

    def post(self, request, movie_id):
        try:
            try:
                movie = Movie.objects.get(tmdb_id=movie_id)
            except Movie.DoesNotExist:
                movie = self.get_movie_from_tmdb(movie_id)

            if not movie:
                return Response({'error': '영화를 찾을 수 없습니다.'}, status=404)

            user = request.user

            if movie in user.favorite_movies.all():
                user.favorite_movies.remove(movie)
                is_favorited = False
            else:
                user.favorite_movies.add(movie)
                is_favorited = True

            try:
                update_user_taste_profile(user)
            except Exception as exc:  # pragma: no cover - non-critical
                logger.warning("Failed to refresh taste profile: %s", exc)

            return Response({
                'is_favorited': is_favorited,
                'message': '좋아요가 추가되었습니다.' if is_favorited else '좋아요가 취소되었습니다.',
            })
        except Exception as e:
            logger.exception("Favorite toggle failed: %s", e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    """내 프로필 정보"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MyProfileSummaryView(APIView):
    """간단 프로필 요약"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSummarySerializer(request.user)
        return Response(serializer.data)


class MyFavoriteMoviesView(APIView):
    """내가 좋아한 영화 목록"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        favorite_movies = request.user.favorite_movies.all().order_by('-id')
        serializer = MovieListSerializer(favorite_movies, many=True)
        return Response(serializer.data)


class UserFavoriteMoviesView(APIView):
    """지정 사용자가 좋아한 영화 목록"""

    permission_classes = [permissions.AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        favorite_movies = user.favorite_movies.all().order_by('-id')
        serializer = MovieListSerializer(favorite_movies, many=True)
        profile_data = UserProfileSerializer(user).data
        return Response({'profile': profile_data, 'movies': serializer.data})


class MyFollowingsListView(APIView):
    """내가 팔로우한 목록"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        followings = request.user.followings.all().order_by('username')
        serializer = FollowSerializer(followings, many=True, context={'request': request})
        return Response(serializer.data)


class MyFollowersListView(APIView):
    """나를 팔로우하는 목록"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        followers = request.user.followers.all().order_by('username')
        serializer = FollowSerializer(followers, many=True, context={'request': request})
        return Response(serializer.data)


class UserListView(APIView):
    """전체 사용자 목록"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.exclude(pk=request.user.pk).order_by('username')
        following_ids = set(request.user.followings.values_list('pk', flat=True))
        follower_ids = set(request.user.followers.values_list('pk', flat=True))
        serializer = UserListSerializer(
            users,
            many=True,
            context={
                'request': request,
                'following_ids': following_ids,
                'follower_ids': follower_ids,
            },
        )
        return Response(serializer.data)


class FollowToggleView(APIView):
    """팔로우 토글"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)

        if target_user == request.user:
            return Response({'error': '본인을 팔로우할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if target_user in user.followings.all():
            user.followings.remove(target_user)
            is_following = False
            message = '팔로우를 취소했습니다.'
        else:
            user.followings.add(target_user)
            is_following = True
            message = '새로 팔로우했습니다.'

        return Response({'username': target_user.username, 'is_following': is_following, 'message': message})


class MyReviewsView(APIView):
    """내가 작성한 리뷰 목록"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reviews = Review.objects.filter(user=request.user).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class CheckFavoriteStatusView(APIView):
    """좋아요 여부 확인"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, movie_id):
        try:
            movie = get_object_or_404(Movie, tmdb_id=movie_id)
            is_favorited = movie in request.user.favorite_movies.all()
            return Response({'is_favorited': is_favorited})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyTasteView(APIView):
    """사용자 취향 요약/임베딩"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = ensure_taste_profile(request.user)
        data = {
            'taste_summary': profile.summary or '',
            'top_genres': profile.top_genres or [],
            'liked_movies_count': profile.liked_movies_count,
            'updated_at': profile.updated_at.isoformat() if profile.updated_at else None,
        }
        if profile.liked_movies_count < MIN_LIKED_FOR_TASTE:
            data['reason'] = 'not_enough_likes'
        return Response(data)


class SimilarUsersByTasteView(APIView):
    """취향 임베딩 기반 유사 사용자 추천"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        k = request.query_params.get('k')
        try:
            k = int(k) if k is not None else 10
        except ValueError:
            k = 10
        k = max(1, min(k, 50))

        base_profile = ensure_taste_profile(request.user)
        base_user = {'id': request.user.id, 'username': request.user.username}
        if base_profile.liked_movies_count < MIN_LIKED_FOR_TASTE or not base_profile.embedding:
            return Response({
                'k': k,
                'base_user': base_user,
                'results': [],
                'reason': 'not_enough_likes',
            })

        base_embedding = base_profile.embedding
        base_like_ids = set(request.user.favorite_movies.values_list('id', flat=True))

        candidates = (
            User.objects.exclude(pk=request.user.pk)
            .filter(taste_profile__liked_movies_count__gte=MIN_LIKED_FOR_TASTE)
            .select_related('taste_profile')
            .prefetch_related('favorite_movies')
        )

        results: List[dict] = []
        for candidate in candidates:
            tp = getattr(candidate, 'taste_profile', None)
            if not tp or not tp.embedding:
                continue
            sim = cosine_similarity(base_embedding, tp.embedding)
            favorite_list = list(candidate.favorite_movies.all())
            candidate_like_ids = {movie.id for movie in favorite_list}
            common = len(base_like_ids.intersection(candidate_like_ids))
            unique_movies = [movie for movie in favorite_list if movie.id not in base_like_ids]
            sample_titles = [movie.title for movie in favorite_list[:5] if movie.title]
            recommendation_sources = unique_movies or favorite_list[:4]
            recommendations = MovieListSerializer(recommendation_sources[:4], many=True).data
            top_genres = tp.top_genres or []
            taste_summary = tp.summary or ''
            liked_movies_count = tp.liked_movies_count or len(favorite_list)
            results.append({
                'user': {'id': candidate.id, 'username': candidate.username, 'bio': candidate.bio},
                'username': candidate.username,
                'bio': candidate.bio,
                'favorite_movie_name': candidate.favorite_movie_name,
                'profile_image': candidate.profile_image,
                'top_genres': top_genres,
                'taste_summary': taste_summary,
                'liked_movies_count': liked_movies_count,
                'sample_titles': sample_titles,
                'recommendations': recommendations,
                'similarity': round(sim, 4),
                'common_likes_count': common,
            })

        results = sorted(results, key=lambda r: r['similarity'], reverse=True)[:k]

        return Response({
            'k': k,
            'base_user': base_user,
            'results': results,
        })


class UserLocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField(allow_null=True, required=True)
    longitude = serializers.FloatField(allow_null=True, required=True)


class MyLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'latitude': user.latitude,
            'longitude': user.longitude,
        })

    def patch(self, request):
        serializer = UserLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.latitude = serializer.validated_data.get('latitude')
        user.longitude = serializer.validated_data.get('longitude')
        user.save(update_fields=['latitude', 'longitude'])
        return Response({
            'latitude': user.latitude,
            'longitude': user.longitude,
        })
