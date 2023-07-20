from rest_framework import serializers
from .models import *

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url = True, required = False)
    comments = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()

    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments, many = True)
        return serializer.data
    
    def get_tag(self, instance):
        tags = instance.tag.all()
        return [tag.name for tag in tags]
    
    def get_like(self, instance):
        likes = instance.like.all()
        return [like.username for like in likes]
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'comments',
            'like',
            'like_cnt',
            'like',
        ]

class PostListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url = True, required = False)
    comments_cnt = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()

    def get_comments_cnt(self, instance):
        return instance.comments.count()
    
    def get_tag(self, instance):
        tags = instance.tag.all()
        return [tag.name for tag in tags]
    
    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'writer',
            'content',
            'created_at',
            'updated_at',
            'image',
            'tag',
            'comments_cnt',
            'like_cnt',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'comments_cnt',
            'like_cnt',
        ]

class CommentSerializer(serializers.ModelSerializer):
    post = serializers.SerializerMethodField(read_only = True)

    def get_post(self, instance):
        return instance.post.title

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = [
            'id',
            'post',
            'created_at',
            'updated_at',
        ]