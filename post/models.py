from django.db import models
from django.contrib.auth.models import User
from basemodel.models import TimestampModel

# Create your models here.
def image_upload_path(instance, filename):
    return f'{instance.id}/{filename}'

class Tag(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 50)

class Post(TimestampModel):
    id = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 50)
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.CharField(max_length = 100)
    tag = models.ManyToManyField(Tag, blank = True)
    image = models.ImageField(upload_to = image_upload_path, blank = True, null = True)

class PostReaction(models.Model):
    REACTION_CHOICES = (('like', 'Like'), ('dislike', 'Dislike'))
    reaction = models.CharField(choices = REACTION_CHOICES, max_length = 10)
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name = 'reactions')
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True)

class Comment(TimestampModel):
    id = models.AutoField(primary_key = True)
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name = 'comments')
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.CharField(max_length = 100)