# Generated by Django 2.2b1 on 2019-06-07 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20190603_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivity',
            name='payload',
            field=models.TextField(blank=True, null=True, verbose_name='payload'),
        ),
    ]