from rest_framework import serializers

from .models import Comment, Like, Post


class CommentSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_image    = serializers.ImageField(source='author.profile_image', read_only=True)

    class Meta:
        model  = Comment
        fields = ['id', 'author_nickname', 'author_image', 'content', 'created_at']
        read_only_fields = ['id', 'author_nickname', 'author_image', 'created_at']


class PostListSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_image    = serializers.ImageField(source='author.profile_image', read_only=True)
    like_count      = serializers.IntegerField(read_only=True)
    comment_count   = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Post
        fields = ['id', 'author_nickname', 'author_image', 'category', 'title', 'content', 'image', 'like_count', 'comment_count', 'view_count', 'created_at']
        read_only_fields = fields


class PostDetailSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_image    = serializers.ImageField(source='author.profile_image', read_only=True)
    like_count      = serializers.IntegerField(read_only=True)
    is_liked        = serializers.SerializerMethodField()
    comments        = CommentSerializer(many=True, read_only=True)

    class Meta:
        model  = Post
        fields = ['id', 'author_nickname', 'author_image', 'category', 'title', 'content', 'image', 'like_count', 'is_liked', 'view_count', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author_nickname', 'author_image', 'like_count', 'is_liked', 'view_count', 'comments', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False


class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Post
        fields = ['category', 'title', 'content', 'image']
