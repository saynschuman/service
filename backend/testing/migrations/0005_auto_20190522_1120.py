# Generated by Django 2.2b1 on 2019-05-22 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0004_unique_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='answer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_answers', to='courses.Answer', verbose_name='Выбранный ответ'),
        ),
    ]
