# Generated by Django 2.2b1 on 2020-10-06 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0039_task_trial_attempts'),
        ('testing', '0014_auto_20201006_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='useranswer',
            name='answers',
            field=models.ManyToManyField(related_name='u_answers', to='courses.Answer', verbose_name='Выбранный ответ'),
        ),
    ]
