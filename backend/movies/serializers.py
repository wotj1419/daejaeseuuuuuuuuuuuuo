from rest_framework import serializers
from .models import Movie

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
