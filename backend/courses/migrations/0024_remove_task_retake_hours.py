# Generated by Django 2.2b1 on 2019-11-19 17:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0023_auto_20191015_2103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='retake_hours',
        ),
    ]
