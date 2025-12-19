from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Movie
from .serializers import MovieRecommendSerializer

class MovieRecommendAPIView(APIView):
    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)
        genres = movie.genres.all()

        # 같은 장르 영화
        candidates = (
            Movie.objects
            .filter(genres__in=genres)
            .exclude(id=movie.id)
            .distinct()
            .order_by('-vote_average', '-popularity')[:10]
        )

        serializer = MovieRecommendSerializer(candidates, many=True)
        return Response(serializer.data)
