# Generated by Django 2.2b1 on 2020-02-19 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0012_auto_20190925_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='answer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='courses.Answer', verbose_name='Выбранный ответ'),
        ),
    ]
