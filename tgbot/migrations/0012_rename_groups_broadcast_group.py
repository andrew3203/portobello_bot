# Generated by Django 4.0.6 on 2022-07-30 19:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0011_rename_group_broadcast_groups'),
    ]

    operations = [
        migrations.RenameField(
            model_name='broadcast',
            old_name='groups',
            new_name='group',
        ),
    ]
