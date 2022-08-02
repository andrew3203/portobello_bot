# Generated by Django 4.0.6 on 2022-08-02 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0013_alter_message_name_alter_message_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broadcast',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='broadcast',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.group'),
        ),
        migrations.AlterField(
            model_name='broadcast',
            name='users',
            field=models.ManyToManyField(blank=True, to='tgbot.user'),
        ),
        migrations.AlterField(
            model_name='file',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='message',
            name='clicks',
            field=models.IntegerField(blank=True, default=0, verbose_name='Кол-во кликов'),
        ),
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='message',
            name='files',
            field=models.ManyToManyField(blank=True, to='tgbot.file', verbose_name='Картинки, Видео, Файлы'),
        ),
        migrations.AlterField(
            model_name='message',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Группы пользователей, для которых доступно данное сообщение. Если группа не выбрана, сообщение доступно всем пользователям.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.group', verbose_name='Группы пользователей'),
        ),
        migrations.AlterField(
            model_name='message',
            name='messages',
            field=models.ManyToManyField(blank=True, help_text='Сообщения, которые могут быть показаны после данного сообщения. Название кнопки должно совпадать с названием сообщения, к которому оно ведет. Кол-во таких сообщений должно быть равно кол-ву кнопок в тексте этого сообщения.', to='tgbot.message', verbose_name='Сообщения'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(help_text='Размер текста не более 4096 символов. Если вы используете кнопки, то их кол-во должно быть равно кол-ву сообщений выбранных ниже. Название кнопки должно совпадать с названием сообщения, к которому оно ведет.', max_length=4096, verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='message',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Username'),
        ),
    ]