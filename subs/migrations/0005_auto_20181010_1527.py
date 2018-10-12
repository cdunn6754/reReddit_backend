# Generated by Django 2.1.2 on 2018-10-10 15:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subs', '0004_auto_20181008_1854'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sub',
            name='members',
        ),
        migrations.AlterField(
            model_name='sub',
            name='moderators',
            field=models.ManyToManyField(related_name='moderated_subs', to=settings.AUTH_USER_MODEL),
        ),
    ]