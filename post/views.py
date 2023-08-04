from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from .serializers import (
    PostSerializer,
    CommentSerializer,
    TagSerializer,
    PostListSerializer,
)
from .models import Post, PostReaction, Comment, Tag
from .permissions import IsOwnerOrReadOnly
from .paginations import PostPagination

from django.shortcuts import get_object_or_404


# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.annotate(
        like_cnt=Count(
            "reactions", filter=Q(reactions__reaction="like"), distinct=True
        ),
        dislike_cnt=Count(
            "reactions", filter=Q(reactions__reaction="dislike"), distinct=True
        ),
        comment_cnt=Count("comments"),
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["writer"]
    search_fields = ["title", "=tag__name"]
    ordering_fields = ["created_at"]
    pagination_class = PostPagination

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def get_permissions(self):
        if self.action in ["update", "destroy", "partial_update"]:
            return [IsOwnerOrReadOnly()]
        elif self.action in ["likes"]:
            return [IsAuthenticated()]
        else:
            return []

    def add_or_change(self, a, b, c):
        add = "like" if c == "like" else "dislike"
        if liked := PostReaction.objects.filter(post=a, user=b).first():
            if liked.reaction == c:
                liked.delete()
            elif liked.reaction != c:
                liked.reaction = "dislike" if liked.reaction == "like" else "like"
                liked.save()
        else:
            PostReaction.objects.create(post=a, user=b, reaction=add)

    @action(methods=["POST"], detail=True)
    def likes(self, request, pk=None):
        post = self.get_object()
        self.add_or_change(post, request.user, "like")
        return Response()

    @action(methods=["POST"], detail=True)
    def dislikes(self, request, pk=None):
        post = self.get_object()
        self.add_or_change(post, request.user, "dislike")
        return Response()

    @action(methods=["GET"], detail=False)
    def top5(self, request):
        movies = self.get_queryset().order_by("-like_cnt")[:5]
        serializer = PostListSerializer(movies, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(writer=request.user)

        post = serializer.instance
        self.handle_tags(post)

        return Response(serializer.data)

    def perform_update(self, serializer):
        post = serializer.save()
        post.tag.clear()
        self.handle_tags(post)

    def handle_tags(self, post):
        words = post.content.split(" ")
        tag_list = []

        for word in words:
            if word[0] == "#":
                tag_list.append(word[1:])

        for t in tag_list:
            tag, boolean = Tag.objects.get_or_create(name=t)
            post.tag.add(tag)

        post.save()


class CommentViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        return []


class PostCommentViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset

    def create(self, request, post_id=None):
        post = get_object_or_404(Post, pk=post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, writer=request.user)
        return Response(serializer.data)


class TagViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "name"
    lookup_url_kwarg = "tag_name"

    def retrieve(self, request, *args, **kwargs):
        tag_name = kwargs.get("tag_name")
        tag = get_object_or_404(Tag, name=tag_name)
        posts = Post.objects.filter(tag__in=[tag])
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
