# Generated by Django 4.2.3 on 2023-07-13 22:50

from django.db import migrations, models
import post.models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=post.models.image_upload_path),
        ),
        migrations.DeleteModel(
            name='PostImage',
        ),
    ]