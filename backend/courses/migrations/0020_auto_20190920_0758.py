# Generated by Django 2.2b1 on 2019-09-20 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0019_course_teacher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
    ]
