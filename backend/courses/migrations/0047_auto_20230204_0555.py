# Generated by Django 2.2.16 on 2023-02-04 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0046_auto_20210607_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialpassing',
            name='text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='materialpassing',
            name='userName',
            field=models.TextField(blank=True),
        ),
    ]
