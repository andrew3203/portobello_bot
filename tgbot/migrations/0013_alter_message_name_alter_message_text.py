# Generated by Django 4.0.6 on 2022-07-31 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0012_rename_groups_broadcast_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='name',
            field=models.CharField(max_length=40, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(max_length=4096, verbose_name='Название'),
        ),
    ]
