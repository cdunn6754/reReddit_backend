# Generated by Django 2.1.2 on 2018-12-14 16:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comments', '0004_comment_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentVotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_type', models.CharField(choices=[('UV', 'upvote'), ('DV', 'downvote')], default='UV', max_length=2)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='comments.Comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='voters',
            field=models.ManyToManyField(related_name='voted_comments', through='comments.CommentVotes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='commentvotes',
            unique_together={('comment', 'user')},
        ),
    ]