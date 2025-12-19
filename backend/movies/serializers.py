from rest_framework import serializers
from .models import Movie

class MovieListSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = (
            'id',
            'title',
            'poster_path',
            'vote_average',
            'avg_rating',
            'review_count',
        )


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = serializers.StringRelatedField(many=True)
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = (
            'id',
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
            'title',
            'poster_path',
            'vote_average',
            'popularity',
        )