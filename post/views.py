from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action

from .serializers import PostSerializer, CommentSerializer, TagSerializer, PostListSerializer
from .models import Post, Comment, Tag
from .permissions import IsOwnerOrReadOnly

from django.shortcuts import get_object_or_404

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostSerializer
    
    @action(methods = ['GET'], detail = True)
    def like(self, request, pk = None):
        post = self.get_object()
        if request.user in post.like.all():
            post.like.remove(request.user)
            post.like_cnt -= 1
            post.save()
        else:
            post.like.add(request.user)
            post.like_cnt += 1
            post.save()
        return Response()

    @action(methods = ['GET'], detail = False)
    def recommend(self, request):
        movies = self.get_queryset().order_by('-like_cnt')[:3]
        serializer = PostListSerializer(movies, many = True)
        return Response(serializer.data)

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

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        return []

class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post = self.kwargs.get('post_id')
        queryset = Comment.objects.filter(post_id = post)
        return queryset
    
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
