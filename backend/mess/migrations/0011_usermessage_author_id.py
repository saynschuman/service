# Generated by Django 2.2.16 on 2022-09-16 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mess', '0010_usermessage_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermessage',
            name='author_id',
            field=models.IntegerField(default=False, null=True),
        ),
    ]
