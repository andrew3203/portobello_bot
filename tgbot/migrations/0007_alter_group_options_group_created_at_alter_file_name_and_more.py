# Generated by Django 4.0.6 on 2022-07-30 12:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0006_file_remove_message_images_remove_message_msg_type_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AddField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(max_length=120, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=32, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='mailing',
            name='name',
            field=models.CharField(max_length=20, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='message',
            name='name',
            field=models.CharField(max_length=20, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(max_length=500, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Имя'),
        ),
    ]