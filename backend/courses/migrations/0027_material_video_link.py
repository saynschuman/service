# Generated by Django 2.2b1 on 2019-11-21 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0026_answer_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='video_link',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на видео'),
        ),
    ]
