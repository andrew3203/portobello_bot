from __future__ import annotations
from email import message
from random import randint
import cyrtranslit

from typing import Union, Optional, Tuple
import re
import json
from datetime import timedelta

from django.db import models
from django.db.models import QuerySet, Manager
from telegram import Update, Video
from telegram.ext import CallbackContext

from dtb.settings import DEBUG
from tgbot.handlers.utils.info import extract_user_data_from_update
from utils.models import CreateUpdateTracker, CreateTracker, nb, GetOrNoneManager

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import redis
from dtb.settings import REDIS_URL


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(
        'Телеграм id',
        primary_key=True
    )
    username = models.CharField(
        'Username',
        max_length=32, **nb
    )
    first_name = models.CharField(
        'Имя',
        max_length=256, **nb
    )
    last_name = models.CharField(
        'Фаммилия',
        max_length=256, **nb
    )
    language_code = models.CharField(
        'Язык',
        max_length=8,
        help_text="Язык приложения телеграм", **nb
    )
    deep_link = models.CharField(
        'Стартовый Код',
        max_length=64, **nb
    )
    is_blocked_bot = models.BooleanField(
        'Бот в блоке',
        default=False
    )
    is_admin = models.BooleanField(
        'Админ',
        default=False
    )

    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'
    
    @staticmethod
    def get_state(user_id):
        r = redis.from_url(REDIS_URL, decode_responses=True)

        if r.exists(user_id):
            message_id = json.loads(r.get(user_id))
            return json.loads(r.get(message_id))

        return None
    
    @staticmethod
    def get_prev_next_states(user_id, msg_text):
        r = redis.from_url(REDIS_URL, decode_responses=True)

        if r.exists(user_id):
            message_id = json.loads(r.get(user_id))
            prev_state = json.loads(r.get(message_id))
            next_state_id = prev_state['ways'].get(
                msg_text, 
                Message.objects.filter(name='Ошибка состояния').first().id
            )
        else:
            prev_state = None
            next_state_id = Message.objects.filter(name='Старт').first().id

        raw_next_sate = r.get(next_state_id)
        next_state = json.loads(raw_next_sate)
        r.setex(user_id, timedelta(hours=10), value=next_state_id)
        
        return prev_state, next_state


    @staticmethod
    def set_state(user_id, message_id):
        r = redis.from_url(REDIS_URL)
        r.setex(user_id, timedelta(hours=10), value=message_id)

    @classmethod
    def get_user_and_created(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(
            user_id=data["user_id"], defaults=data)

        if created:
            # Save deep_link to User model
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                # you can't invite yourself
                u.deep_link = payload
                u.save()

        return u, created

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext) -> User:
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, username_or_user_id: Union[str, int]) -> Optional[User]:
        """ Search user in DB, return User or None if not found """
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"


class Group(CreateTracker):
    name = models.CharField(
        'Название',
        max_length=32
    )
    users = models.ManyToManyField(User)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name}'


def user_directory_path(instance, filename):
    base = 'abcdefghijklomopqrstuvwsynz'
    pre = ''.join([base[randint(0, 25)] for _ in range(3)])
    name = instance.name.replace(' ', '-')
    new_filename = cyrtranslit.to_latin(name, 'ru')
    new_filename = f"{new_filename}__{pre}.{filename.split('.')[-1]}".lower()
    return f'messages/{new_filename}'


class File(CreateTracker):
    name = models.CharField(
        'Название',
        max_length=120,
    )
    tg_id = models.CharField(
        'Телеграм id',
        max_length=100, default=None, **nb
    )
    file = models.FileField(
        'Файл, видео',
        upload_to=user_directory_path,
        null=True
    )

    class Meta:
        verbose_name = 'Медиа файл'
        verbose_name_plural = 'Медиа файлы'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name}, {self.tg_id}'


class MessageType(models.TextChoices):
    SIMPLE_TEXT = 'SIMPLE_TEXT', 'Простой текст'
    POLL = 'POLL', 'Опрос'
    KEYBOORD_BTN = 'KEYBOORD_BTN', 'Кнопка'
    FLY_BTN = 'FLY_BTN', 'Чат. Кнопка'


class Message(CreateUpdateTracker):
    name = models.CharField(
        'Название',
        max_length=40,
    )
    text = models.TextField(
        'Текст',
        max_length=4096,
        help_text='Размер текста не более 4096 символов. Если вы используете кнопки, то их кол-во должно быть равно кол-ву сообщений выбранных ниже. Название кнопки должно совпадать с названием сообщения, к которому оно ведет.'
    )
    message_type = models.CharField(
        'Тип Сообщения',
        max_length=25,
        choices=MessageType.choices,
        default=MessageType.SIMPLE_TEXT,
    )
    clicks = models.IntegerField(
        'Кол-во кликов',
        default=0,
        blank=True
    )
    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Группы пользователей',
        help_text='Группы пользователей, для которых доступно данное сообщение. Если группа не выбрана, сообщение доступно всем пользователям.'
    )
    messages = models.ManyToManyField(
        'self',
        blank=True,
        verbose_name='Сообщения',
        help_text='Сообщения, которые могут быть показаны после данного сообщения. Название кнопки должно совпадать с названием сообщения, к которому оно ведет. Кол-во таких сообщений должно быть равно кол-ву кнопок в тексте этого сообщения.'
    )
    files = models.ManyToManyField(
        File,
        blank=True,
        verbose_name='Картинки, Видео, Файлы'
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name}'
    
    def _gen_msg_dict(self):
        messages = self.messages.values_list('name', 'id')
        messages = [(k.lower().replace(' ', ''), v) for k, v in messages]
        return dict(messages)

    def parse_text(self) -> dict:
        msg_dict = self._gen_msg_dict()
        regex = r"(\[[^\[\]]+\]\([^\(\)]+\)\s*\n)|(\[[^\[\]]+\]\s*\n)|(\[[^\[\]]+\]\([^\(\)]+\))|(\[[^\[\]]+\])"
        # group 1 - элемент кнопки с сылкой (с \n)
        # group 2 - обычный элемент кнопки опроса (с \n)

        # group 3 - элемент кнопки с сылкой (без \n)
        # group 4 - обычный элемент кнопки опроса (без \n)
        self.text = re.sub('\\r', '', self.text)
        matches = re.finditer(regex, self.text, re.MULTILINE)
        message_ids = self.messages.values_list('id', flat=True)

        res = [[]]
        ways = {}
        end_text = 100000
        for match in matches:
            group = match.group()
            end_text = min(end_text, match.start())
            groupNum = 1 + list(match.groups()).index(group)
            if groupNum in (1, 3):
                btn, link = group.split('](')
                btn = btn[1:]
                link = re.sub('(\)\s*)|([\)\n])', '', link)
            else:
                btn = re.sub('(\]\s*)|([\[\]\n])', '', group)
                link = None

            res[-1].append((btn, link))
            if groupNum in (1, 2):
                res.append([])

            if groupNum in (2, 4):
                btn_name = btn.lower().replace(' ', '')
                ways[btn_name] = msg_dict[btn_name]


        return {
            'message_type': self.message_type,
            'text': self.text[:end_text],
            'markup': res,
            'ways': ways
        }


    @staticmethod
    def get_structure():
        d = {}
        for o in Message.objects.all():
            data = o.parse_text()
            d[o.id] = json.dumps({
                'messages': list(o.messages.values_list('id', flat=True)),
                'text': data['text'],
                'ways': data['ways'],
                'markup': data['markup'],
                'message_type': data['message_type'],
            }, ensure_ascii=False)

        return d


class Poll(CreateUpdateTracker):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name='Сообщение'

    )
    answers = models.TextField(
        max_length=500,
        verbose_name='Ответы',
        blank=True, null=True
    )

    class Meta:
        verbose_name = 'Результат опроса'
        verbose_name_plural = 'Результаты опросов'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Ответы на опрос: {self.message.name}'


class Broadcast(CreateTracker):
    name = models.CharField(
        'Название',
        max_length=20,
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        null=True
    )
    users = models.ManyToManyField(
        User,
        blank=True,
    )
    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name}'

    def get_users(self):
        ids1 = self.users.values_list('user_id', flat=True)
        ids2 = self.group.users.values_list('user_id', flat=True)
        return list(set(ids1+ids2))


@receiver(post_delete, sender=Message)
@receiver(post_save, sender=Message)
def set_states(sender, **kwargs):
    r = redis.from_url(REDIS_URL)
    r.ping()
    d = Message.get_structure()
    print(d)
    r.mset(d)
