# Generated by Django 2.2b1 on 2019-11-21 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0025_task_retake_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='rank',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Очереднось показа'),
        ),
    ]
