# Generated by Django 2.2b1 on 2019-08-14 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_user_old_password'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useractivity',
            old_name='user_agent',
            new_name='headers',
        ),
    ]
