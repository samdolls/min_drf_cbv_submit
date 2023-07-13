from rest_framework import serializers
from .models import *

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only = True)
    created_at = serializers.CharField(read_only = True)
    updated_at = serializers.CharField(read_only = True)
    image = serializers.ImageField(use_url = True, required = False)

    comments = serializers.SerializerMethodField(read_only = True)
    tag = serializers.SerializerMethodField()

    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments, many = True)
        return serializer.data
    
    def get_tag(self, instance):
        tags = instance.tag.all()
        return [tag.name for tag in tags]
    
    class Meta:
        model = Post
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only = True)
    post = serializers.CharField(read_only = True)
    created_at = serializers.CharField(read_only = True)
    updated_at = serializers.CharField(read_only = True)

    post = serializers.SerializerMethodField(read_only = True)

    def get_post(self, instance):
        return instance.post.title

    class Meta:
        model = Comment
        fields = '__all__'