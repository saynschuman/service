# Generated by Django 2.2b1 on 2019-05-16 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_bookmark_model'),
        ('testing', '0003_auto_20190507_1554'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='useranswer',
            unique_together={('passing', 'question', 'answer')},
        ),
    ]