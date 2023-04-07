# Generated by Django 2.2b1 on 2019-06-24 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_auto_20190618_1711'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['rank', 'title', '-created'], 'verbose_name': 'Задание', 'verbose_name_plural': 'Задания'},
        ),
        migrations.AddField(
            model_name='task',
            name='rank',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Очереднось показа'),
        ),
    ]
