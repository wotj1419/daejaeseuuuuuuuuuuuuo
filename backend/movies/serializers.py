from rest_framework import serializers
from .models import Movie, Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')

class MovieListSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    genres = serializers.StringRelatedField(many=True)

    class Meta:
        model = Movie
        fields = (
            'id',
            'tmdb_id',
            'title',
            'poster_path',
            'vote_average',
            'popularity',
            'overview',
            'avg_rating',
            'review_count',
            'genres',
        )


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = serializers.StringRelatedField(many=True)
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = (
            'id',
            'tmdb_id',
            'title',
            'original_title',
            'overview',
            'release_date',
            'poster_path',
            'backdrop_path',
            'vote_average',
            'avg_rating',
            'review_count',
            'genres',
        )
        
class MovieRecommendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = (
            'id',
            'tmdb_id',
            'title',
            'poster_path',
            'vote_average',
            'popularity',
        )