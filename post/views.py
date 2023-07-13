from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins

from .serializers import PostSerializer, CommentSerializer, TagSerializer
from .models import Post, Comment, Tag

from django.shortcuts import get_object_or_404

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def create(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_create(serializer)

        post = serializer.instance
        self.handle_tags(post)
        
        return Response(serializer.data)
    
    def perform_update(self, serializer):
        post = serializer.save()
        post.tag.clear()
        self.handle_tags(post)
    
    def handle_tags(self, post):
        words = post.content.split(' ')
        tag_list = []

        for word in words:
            if word[0] == '#':
                tag_list.append(word[1:])

        for t in tag_list:
            tag, boolean = Tag.objects.get_or_create(name = t)
            post.tag.add(tag)

        post.save()

class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def list(self, request, post_id = None):
        post = get_object_or_404(Post, pk = post_id)
        queryset = self.filter_queryset(self.get_queryset().filter(post = post))
        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)
    
    def create(self, request, post_id = None):
        post = get_object_or_404(Post, pk = post_id)
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save(post = post)
        return Response(serializer.data)
    
class TagViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "name"
    lookup_url_kwarg = "tag_name"

    def retrieve(self, request, *args, **kwargs):
        tag_name = kwargs.get("tag_name")
        tag = get_object_or_404(Tag, name = tag_name)
        posts = Post.objects.filter(tag__in = [tag])
        serializer = PostSerializer(posts, many = True)
        return Response(serializer.data)
