from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.SerializerMethodField()
    movie_title = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            'id',
            'movie',
            'user',
            'username',
            'movie_title',
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
