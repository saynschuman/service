# Generated by Django 2.2b1 on 2020-02-12 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_userdayactivity_course_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='teacher_chat',
            field=models.BooleanField(default=False, verbose_name='Чат с преподавателем'),
        ),
    ]