# Generated by Django 3.2.12 on 2022-04-28 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_mark_working_plan'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_type', models.CharField(choices=[('ДЗ', 'Домашняя работа'), ('КР', 'Контрольная работа'), ('СР', 'Самостоятельная работа'), ('ОТВ', 'Работа на уроке')], max_length=32, verbose_name='Тип работы')),
            ],
        ),
        migrations.RemoveField(
            model_name='mark',
            name='working_plan',
        ),
        migrations.AddField(
            model_name='mark',
            name='work_type',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='main.worktype', verbose_name='Тип работы'),
        ),
        migrations.AlterField(
            model_name='workingplan',
            name='plan_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.worktype', verbose_name='Тип работы'),
        ),
    ]
