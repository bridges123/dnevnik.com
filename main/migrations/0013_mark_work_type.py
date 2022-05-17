# Generated by Django 3.2.12 on 2022-04-28 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_remove_mark_work_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='mark',
            name='work_type',
            field=models.CharField(choices=[('ДЗ', 'Домашняя работа'), ('КР', 'Контрольная работа'), ('СР', 'Самостоятельная работа'), ('ОТВ', 'Работа на уроке')], default=None, max_length=32, verbose_name='Тип работы'),
        ),
    ]