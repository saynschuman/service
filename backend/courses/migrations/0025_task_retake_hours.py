# Generated by Django 2.2b1 on 2019-11-19 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0024_remove_task_retake_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='retake_hours',
            field=models.TimeField(default='01:00:00', verbose_name='Интервала пересдачи'),
        ),
    ]
