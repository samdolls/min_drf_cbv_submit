from django.db import models
from django.contrib.auth.models import User

# Create your models here.
def image_upload_path(instance, filename):
    return f'{instance.id}/{filename}'

class Tag(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 50)

class Post(models.Model):
    id = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 50)
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.CharField(max_length = 100)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    tag = models.ManyToManyField(Tag, blank = True)
    image = models.ImageField(upload_to = image_upload_path, blank = True, null = True)
    like = models.ManyToManyField(User, blank = True, related_name = 'likes')
    like_cnt = models.PositiveSmallIntegerField(default = 0)

class Comment(models.Model):
    id = models.AutoField(primary_key = True)
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name = 'comments')
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.CharField(max_length = 100)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)