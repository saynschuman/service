# Generated by Django 2.2.16 on 2022-08-09 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_user_webinars'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_active',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Последняя активность'),
        ),
    ]
