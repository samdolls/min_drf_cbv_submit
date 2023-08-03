from rest_framework import serializers
from .models import *

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url = True, required = False)
    writer = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    like_cnt = serializers.IntegerField(required = False)
    dislike_cnt = serializers.IntegerField(required = False)
    comment_cnt = serializers.IntegerField(required = False)

    def get_writer(self, instance):
        return instance.writer.username

    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments, many = True)
        return serializer.data
    
    def get_tag(self, instance):
        tags = instance.tag.all()
        return [tag.name for tag in tags]
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            'id',
            'writer',
            'like_cnt',
            'dislike_cnt',
            'comment_cnt',
            'created_at',
            'updated_at',
            'comments',
            'like',
        ]

class PostListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url = True, required = False)
    writer = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    like_cnt = serializers.IntegerField(required = False)
    dislike_cnt = serializers.IntegerField(required = False)
    comment_cnt = serializers.IntegerField(required = False)

    def get_writer(self, instance):
        return instance.writer.username
    
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
            'like_cnt',
            'dislike_cnt',
            'comment_cnt',
            'created_at',
            'updated_at',
            'image',
            'tag',
        ]
        read_only_fields = [
            'id',
            'like_cnt',
            'dislike_cnt',
            'comment_cnt',
            'created_at',
            'updated_at',
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