# Generated by Django 3.2.12 on 2022-04-12 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20220412_1711'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subject',
            old_name='subject_name',
            new_name='name',
        ),
    ]