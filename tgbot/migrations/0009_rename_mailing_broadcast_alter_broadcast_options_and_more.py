# Generated by Django 4.0.6 on 2022-07-30 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0008_alter_file_options_file_created_at'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Mailing',
            new_name='Broadcast',
        ),
        migrations.AlterModelOptions(
            name='broadcast',
            options={'ordering': ['-created_at'], 'verbose_name': 'Рассылка', 'verbose_name_plural': 'Рассылки'},
        ),
        migrations.AlterModelOptions(
            name='file',
            options={'ordering': ['-created_at'], 'verbose_name': 'Медиа файл', 'verbose_name_plural': 'Медиа файлы'},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ['-created_at'], 'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-created_at'], 'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-created_at'], 'verbose_name': 'Клиент', 'verbose_name_plural': 'Клиенты'},
        ),
    ]
