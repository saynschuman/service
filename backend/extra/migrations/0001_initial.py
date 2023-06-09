# Generated by Django 2.2.16 on 2020-11-03 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLogger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Сообщение')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
            ],
            options={
                'verbose_name': 'Лог ошибок',
                'verbose_name_plural': 'Логи ошибок',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='EmailSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255, verbose_name='E-mail')),
                ('password', models.CharField(max_length=255, verbose_name='Пароль')),
                ('port', models.PositiveSmallIntegerField(default=587, verbose_name='Порт')),
                ('tls', models.BooleanField(default=True, verbose_name='Использовать TLS')),
                ('host', models.CharField(max_length=255, verbose_name='Хост провайдера')),
            ],
            options={
                'verbose_name': 'Глобальные настройки почты',
            },
        ),
    ]
