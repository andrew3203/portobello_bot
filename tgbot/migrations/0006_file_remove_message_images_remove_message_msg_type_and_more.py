# Generated by Django 4.0.6 on 2022-07-30 10:54

from django.db import migrations, models
import tgbot.models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0005_mailing_group_alter_message_images_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=120, null=True, verbose_name='Название')),
                ('tg_id', models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='Телеграм id')),
                ('video', models.FileField(null=True, upload_to=tgbot.models.user_directory_path, verbose_name='Файл, видео')),
            ],
        ),
        migrations.RemoveField(
            model_name='message',
            name='images',
        ),
        migrations.RemoveField(
            model_name='message',
            name='msg_type',
        ),
        migrations.RemoveField(
            model_name='message',
            name='vedios',
        ),
        migrations.AddField(
            model_name='message',
            name='message_type',
            field=models.CharField(choices=[('SIMPLE_TEXT', 'Простой текст'), ('POLL', 'Опрос'), ('KEYBOORD_BTN', 'Кнопка'), ('FLY_BTN', 'Чат. Кнопка')], default='SIMPLE_TEXT', max_length=25, verbose_name='Тип Сообщения'),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='mailing',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='message',
            name='clicks',
            field=models.IntegerField(default=0, verbose_name='Кол-во кликов'),
        ),
        migrations.AlterField(
            model_name='message',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='user',
            name='deep_link',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Стартовый Код'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=256, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Админ'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_blocked_bot',
            field=models.BooleanField(default=False, verbose_name='Бот в блоке'),
        ),
        migrations.AlterField(
            model_name='user',
            name='language_code',
            field=models.CharField(blank=True, help_text='Язык приложения телеграм', max_length=8, null=True, verbose_name='Язык'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Фаммилия'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.PositiveBigIntegerField(primary_key=True, serialize=False, verbose_name='Телеграм id'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Username пользователя'),
        ),
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.DeleteModel(
            name='Video',
        ),
        migrations.AddField(
            model_name='message',
            name='files',
            field=models.ManyToManyField(to='tgbot.file', verbose_name='Картинки, Видео, Файлы'),
        ),
    ]