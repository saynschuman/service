# Generated by Django 2.2b1 on 2020-06-25 12:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mess', '0008_usermessage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='is_read',
        ),
    ]