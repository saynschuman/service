# Generated by Django 2.2b1 on 2020-02-16 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0034_auto_20200210_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='passing',
            name='is_trial',
            field=models.BooleanField(default=False, verbose_name='Пробная попытка'),
        ),
    ]