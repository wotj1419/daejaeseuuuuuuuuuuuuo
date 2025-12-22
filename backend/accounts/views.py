from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, serializers
from django.conf import settings
from django.shortcuts import get_object_or_404
import requests
from .models import User
from movies.models import Movie
from movies.serializers import MovieListSerializer
from reviews.models import Review
from reviews.serializers import ReviewSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'bio', 'favorite_movie_name')
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
        fields = ('username', 'bio', 'favorite_movie_name', 'is_following')

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
    """영화 좋아요 토글 (추가/제거)"""
    permission_classes = [permissions.IsAuthenticated]

    def get_movie_from_tmdb(self, tmdb_id):
        api_key = settings.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {
            'api_key': api_key,
            'language': 'ko-KR',
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # 장르 처리
                genres = []
                if 'genres' in data:
                    from movies.models import Genre  # Import here to avoid circular import if necessary
                    for g in data['genres']:
                         genre, created = Genre.objects.get_or_create(
                             name=g['name']
                        )
                         genres.append(genre)

                # 영화 저장
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
                    }
                )
                
                if created:
                     movie.genres.set(genres)
                
                return movie
        except Exception as e:
            print(f"Error fetching from TMDB: {e}")
            return None
        return None

    def post(self, request, movie_id):
        try:
            # 먼저 DB에서 찾기
            try:
                movie = Movie.objects.get(tmdb_id=movie_id)
            except Movie.DoesNotExist:
                # DB에 없으면 TMDB에서 가져오기
                movie = self.get_movie_from_tmdb(movie_id)
                
            if not movie:
                return Response({'error': '영화를 찾을 수 없습니다.'}, status=404)

            user = request.user

            if movie in user.favorite_movies.all():
                # 이미 좋아요한 영화면 제거
                user.favorite_movies.remove(movie)
                is_favorited = False
            else:
                # 좋아요 추가
                user.favorite_movies.add(movie)
                is_favorited = True

            return Response({
                'is_favorited': is_favorited,
                'message': '좋아요가 추가되었습니다.' if is_favorited else '좋아요가 취소되었습니다.'
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ProfileView(APIView):
    """현재 로그인한 유저의 프로필 정보"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MyProfileSummaryView(APIView):
    """사용자 대시보드용 요약 정보"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSummarySerializer(request.user)
        return Response(serializer.data)


class MyFavoriteMoviesView(APIView):
    """내가 좋아요한 영화 목록"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        favorite_movies = user.favorite_movies.all().order_by('-id')
        serializer = MovieListSerializer(favorite_movies, many=True)
        return Response(serializer.data)


class UserFavoriteMoviesView(APIView):
    """특정 유저가 좋아요한 영화 목록"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        favorite_movies = user.favorite_movies.all().order_by('-id')
        serializer = MovieListSerializer(favorite_movies, many=True)
        profile_data = UserProfileSerializer(user).data
        return Response({
            'profile': profile_data,
            'movies': serializer.data,
        })


class MyFollowingsListView(APIView):
    """현재 유저의 팔로잉 목록"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        followings = request.user.followings.all().order_by('username')
        serializer = FollowSerializer(followings, many=True, context={'request': request})
        return Response(serializer.data)


class MyFollowersListView(APIView):
    """현재 유저를 팔로우하는 유저 목록"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        followers = request.user.followers.all().order_by('username')
        serializer = FollowSerializer(followers, many=True, context={'request': request})
        return Response(serializer.data)


class UserListView(APIView):
    """전체 사용자 목록 (팔로우/언팔로우용)"""
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
            }
        )
        return Response(serializer.data)


class FollowToggleView(APIView):
    """팔로우/언팔로우 토글"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)

        if target_user == request.user:
            return Response(
                {'error': '본인은 팔로우할 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if target_user in user.followings.all():
            user.followings.remove(target_user)
            is_following = False
            message = '팔로잉을 취소했습니다.'
        else:
            user.followings.add(target_user)
            is_following = True
            message = '새로 팔로우했습니다.'

        return Response({
            'username': target_user.username,
            'is_following': is_following,
            'message': message,
        })


class MyReviewsView(APIView):
    """내가 작성한 리뷰 목록"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        reviews = Review.objects.filter(user=user).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class CheckFavoriteStatusView(APIView):
    """영화가 좋아요되었는지 확인"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, movie_id):
        try:
            movie = get_object_or_404(Movie, tmdb_id=movie_id)
            user = request.user
            is_favorited = movie in user.favorite_movies.all()
            
            return Response({'is_favorited': is_favorited})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
