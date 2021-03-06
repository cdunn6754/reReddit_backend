# Generated by Django 2.1.2 on 2018-10-06 22:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=150)),
                ('admins', models.ManyToManyField(related_name='sub', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
