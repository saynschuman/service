# Generated by Django 2.2.16 on 2022-09-16 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mess', '0011_usermessage_author_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermessage',
            name='chat_status',
            field=models.IntegerField(default=False, null=True),
        ),
    ]
