from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from movies.models import Movie
from movies.serializers import MovieListSerializer
from reviews.models import Review
from reviews.serializers import ReviewSerializer


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


class MyFavoriteMoviesView(APIView):
    """내가 좋아요한 영화 목록"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        favorite_movies = user.favorite_movies.all().order_by('-id')
        serializer = MovieListSerializer(favorite_movies, many=True)
        return Response(serializer.data)


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
