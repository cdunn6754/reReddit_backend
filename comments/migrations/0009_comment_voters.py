# Generated by Django 2.1.2 on 2018-12-16 17:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('votes', '0001_initial'),
        ('comments', '0008_auto_20181216_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='voters',
            field=models.ManyToManyField(related_name='voted_comments', through='votes.CommentVote', to=settings.AUTH_USER_MODEL),
        ),
    ]
