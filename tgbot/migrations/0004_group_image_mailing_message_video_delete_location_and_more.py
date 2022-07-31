# Generated by Django 4.0.6 on 2022-07-30 09:43

from django.db import migrations, models
import django.db.models.deletion
import tgbot.models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0003_rm_unused_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('users', models.ManyToManyField(to='tgbot.user')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('tg_id', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('image', models.ImageField(null=True, upload_to=tgbot.models.user_directory_path)),
            ],
        ),
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('name', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=20, null=True)),
                ('text', models.TextField(blank=True, max_length=500, null=True)),
                ('msg_type', models.TextField()),
                ('clicks', models.IntegerField(default=0)),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.group')),
                ('images', models.ManyToManyField(blank=True, null=True, to='tgbot.image')),
                ('messages', models.ManyToManyField(blank=True, null=True, to='tgbot.message')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('tg_id', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('video', models.FileField(null=True, upload_to=tgbot.models.user_directory_path)),
            ],
        ),
        migrations.DeleteModel(
            name='Location',
        ),
        migrations.AddField(
            model_name='message',
            name='vedios',
            field=models.ManyToManyField(blank=True, null=True, to='tgbot.video'),
        ),
        migrations.AddField(
            model_name='mailing',
            name='message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.message'),
        ),
        migrations.AddField(
            model_name='mailing',
            name='users',
            field=models.ManyToManyField(to='tgbot.user'),
        ),
    ]