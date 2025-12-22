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


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'bio', 'favorite_movie_name')


class UserListSerializer(serializers.ModelSerializer):
    is_friend = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'bio', 'favorite_movie_name', 'is_friend')

    def get_is_friend(self, obj):
        friend_ids = self.context.get('friend_ids')
        if friend_ids is not None:
            return obj.pk in friend_ids

        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if user and user.is_authenticated:
            return user.friends.filter(pk=obj.pk).exists()
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


class MyFriendsListView(APIView):
    """현재 유저의 친구 목록"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        friends = request.user.friends.all().order_by('username')
        serializer = FriendSerializer(friends, many=True)
        return Response(serializer.data)


class UserListView(APIView):
    """전체 사용자 목록 (친구 추가용)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.exclude(pk=request.user.pk).order_by('username')
        friend_ids = set(request.user.friends.values_list('pk', flat=True))
        serializer = UserListSerializer(
            users,
            many=True,
            context={'request': request, 'friend_ids': friend_ids}
        )
        return Response(serializer.data)


class FriendToggleView(APIView):
    """친구 등록/삭제 토글"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)

        if target_user == request.user:
            return Response(
                {'error': '본인은 친구로 추가할 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if target_user in user.friends.all():
            user.friends.remove(target_user)
            is_friend = False
            message = '친구 목록에서 제거되었습니다.'
        else:
            user.friends.add(target_user)
            is_friend = True
            message = '친구로 등록되었습니다.'

        return Response({
            'username': target_user.username,
            'is_friend': is_friend,
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
