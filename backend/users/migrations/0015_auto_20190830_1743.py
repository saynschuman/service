# Generated by Django 2.2b1 on 2019-08-30 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20190830_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='group_chat',
            field=models.BooleanField(default=False, verbose_name='Чат с одногрупниками'),
        ),
    ]
