from rest_framework import serializers
from accounts.models import User
from .models import BoardPost


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
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'board_type',
            'author_username',
            'invited',
            'created_at',
            'updated_at',
        )

    def get_invited(self, obj):
        return [user.username for user in obj.invited_users.all()]

    def validate_invited_usernames(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            raise serializers.ValidationError('로그인이 필요합니다.')

        following_ids = set(user.followings.values_list('pk', flat=True))
        for invited_user in value:
            if invited_user.pk not in following_ids:
                raise serializers.ValidationError(f'{invited_user.username}님은 팔로잉 중인 사용자만 초대할 수 있습니다.')
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
