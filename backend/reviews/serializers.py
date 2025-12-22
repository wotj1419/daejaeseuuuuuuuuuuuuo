from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.SerializerMethodField()
    movie_title = serializers.SerializerMethodField()
    movie_tmdb_id = serializers.SerializerMethodField()
    movie_poster_path = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            'id',
            'movie',
            'user',
            'username',
            'movie_title',
            'movie_tmdb_id',
            'movie_poster_path',
            'content',
            'rating',
            'created_at',
            'updated_at',
        )
    
    def get_username(self, obj):
        """사용자 닉네임 반환 (익명 리뷰 처리)"""
        if obj.user:
            return obj.user.username
        return '익명'

    def get_movie_title(self, obj):
        return obj.movie.title

    def get_movie_tmdb_id(self, obj):
        return getattr(obj.movie, 'tmdb_id', None)

    def get_movie_poster_path(self, obj):
        return getattr(obj.movie, 'poster_path', '')
