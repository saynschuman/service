# Generated by Django 2.2b1 on 2019-06-03 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='end_course',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время окончания курса'),
        ),
        migrations.AddField(
            model_name='user',
            name='start_course',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время начала курса'),
        ),
    ]
