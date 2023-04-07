# Generated by Django 2.2b1 on 2019-08-30 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_delete_debugmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='group_chat',
            field=models.BooleanField(default=True, verbose_name='Чат с одногрупниками'),
        ),
        migrations.AddField(
            model_name='user',
            name='teacher_chat',
            field=models.BooleanField(default=True, verbose_name='Чат с преподавателем'),
        ),
        migrations.AddField(
            model_name='user',
            name='tech_chat',
            field=models.BooleanField(default=True, verbose_name='Чат с тех. поддержкой'),
        ),
    ]
