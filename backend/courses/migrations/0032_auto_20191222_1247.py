# Generated by Django 2.2b1 on 2019-12-22 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0031_auto_20191218_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passing',
            name='message',
        ),
        migrations.AlterField(
            model_name='passing',
            name='success_passed',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Тест пройден успешно'), (1, 'На проверке'), (2, 'Превышено допустимое время прохождения'), (3, 'Превышено допустимое кол-во попыток'), (4, 'Процент прохождения не набран')], default=1, verbose_name='Статус прохождения'),
        ),
    ]