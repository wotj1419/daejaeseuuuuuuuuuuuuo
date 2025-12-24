from rest_framework import serializers
from django.db.models import Q
from accounts.models import User
from .models import BoardPost, BoardPostComment


class BoardCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = BoardPostComment
        fields = (
            'id',
            'author_username',
            'content',
            'created_at',
        )


class BoardPostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    invited_usernames = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all(),
        required=False,
        write_only=True,
    )
    invited = serializers.SerializerMethodField()
    view_count = serializers.SerializerMethodField()
    recommendation_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    comments = BoardCommentSerializer(many=True, read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = BoardPost
        fields = (
            'id',
            'title',
            'content',
            'movie_title',
            'board_type',
            'author_username',
            'invited',
            'invited_usernames',
            'view_count',
            'recommendation_count',
            'comment_count',
            'comments',
            'created_at',
            'updated_at',
            'latitude',
            'longitude',
            'distance_km',
        )
        read_only_fields = (
            'id',
            'board_type',
            'author_username',
            'invited',
            'created_at',
            'updated_at',
            'view_count',
            'recommendation_count',
            'comment_count',
            'comments',
            'distance_km',
        )

    def get_invited(self, obj):
        return [user.username for user in obj.invited_users.all()]

    def get_view_count(self, obj):
        return getattr(obj, 'view_count', 0) or 0

    def get_recommendation_count(self, obj):
        return getattr(obj, 'recommendation_count', 0) or 0

    def get_comment_count(self, obj):
        return getattr(obj, 'comment_count', 0) or 0

    def get_distance_km(self, obj):
        distance = getattr(obj, 'distance_km', None)
        if distance is None:
            return None
        return round(distance, 2)

    def validate_invited_usernames(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            raise serializers.ValidationError('로그인이 필요합니다.')

        # Check if this is a message in an existing chat room
        title = self.initial_data.get('title')
        if title:
            existing_posts = BoardPost.objects.filter(
                board_type=BoardPost.BOARD_TYPE_FRIEND,
                title=title
            ).filter(
                Q(author=user) | Q(invited_users=user)
            ).distinct()
            
            if existing_posts.exists():
                # Get all participants from existing chat room
                existing_participants = set()
                for post in existing_posts:
                    existing_participants.add(post.author.pk)
                    existing_participants.update(post.invited_users.values_list('pk', flat=True))
                
                # Allow existing participants without following check
                invited_pks = {u.pk for u in value}
                if invited_pks.issubset(existing_participants):
                    return value

        # For new chat rooms, require following
        following_ids = set(user.followings.values_list('pk', flat=True))
        for invited_user in value:
            if invited_user.pk not in following_ids:
                raise serializers.ValidationError(
                    f'{invited_user.username}님은 팔로잉 중인 사용자만 초대할 수 있습니다.'
                )
        return value

    def create(self, validated_data):
        invited_users = validated_data.pop('invited_usernames', [])
        post = BoardPost.objects.create(**validated_data)
        if invited_users:
            post.invited_users.set(invited_users)
        return post

    def update(self, instance, validated_data):
        invited_users = validated_data.pop('invited_usernames', None)
        instance = super().update(instance, validated_data)
        if invited_users is not None:
            instance.invited_users.set(invited_users)
        return instance
