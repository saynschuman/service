# Generated by Django 2.2b1 on 2019-04-24 11:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attempts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Время изменения')),
                ('num_attempts', models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Кол-во попыток')),
            ],
            options={
                'verbose_name': 'Кол-во попыток',
                'verbose_name_plural': 'Кол-во попыток',
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Время изменения')),
                ('text', models.TextField(verbose_name='Ответ в произвольной форме')),
                ('is_true', models.BooleanField(default=False, verbose_name='Правильный ответ')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='courses.Answer', verbose_name='Выбранный ответ')),
                ('passing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='courses.Passing', verbose_name='Прохождение теста')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='courses.Question', verbose_name='Вопрос')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
                'ordering': ['-created'],
            },
        ),
    ]
