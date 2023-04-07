# Generated by Django 2.2b1 on 2020-01-18 07:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mess', '0004_auto_20200118_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='chat_images/', validators=[django.core.validators.MaxLengthValidator(1048576), django.core.validators.FileExtensionValidator(allowed_extensions=('png', 'jpeg', 'jpg', 'bmp'))], verbose_name='Изображение'),
        ),
    ]