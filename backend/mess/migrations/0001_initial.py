# Generated by Django 2.2b1 on 2019-04-24 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Время изменения')),
                ('chat_status', models.SmallIntegerField(choices=[(0, 'Чат с тех. поддержкой'), (1, 'Чат с преподавателем'), (2, 'Чат с одногруппниками')], default=0, verbose_name='Тип чата')),
            ],
            options={
                'verbose_name': 'Чат',
                'verbose_name_plural': 'Чаты',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Время изменения')),
                ('mess', models.TextField(verbose_name='Сообщение')),
                ('is_read', models.BooleanField(default=False, verbose_name='Прочитанное сообщение')),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='mess.Chat', verbose_name='Чат')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
    ]
