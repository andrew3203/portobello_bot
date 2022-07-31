from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from dtb.settings import DEBUG

from django.contrib.auth.models import Group as gp
from django.contrib.auth.models import User as DjangoUser

from django.urls import reverse


from tgbot.models import *
from tgbot import forms

from tgbot.tasks import broadcast_message
from tgbot.handlers.broadcast_message.utils import _send_message

admin.site.unregister(gp)
admin.site.unregister(DjangoUser)


admin.site.site_header = 'Portobello Bot Админ панель'
admin.site.index_title = 'Portobello Bot Администратор'
admin.site.site_title = 'Admin'

@admin.register(DjangoUser)
class DjangoAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'first_name',
        'is_staff', 'date_joined'
    ]
    list_filter = ["is_active", "is_staff"]
    search_fields = ('username', 'email')
    fieldsets = (
        ('О пользователе', {
            'fields': (
                ("username",),
                ("password",),
            ),
        }),
        ('Персональная информация', {
            'fields': (
                ("first_name"),
                ('last_name',),
                ("email",)
            ),
        }),
        ('Дополнительная информация', {
            'fields': (
                ("is_active",),
                ("is_staff", ),
                ('is_superuser',)
            ),
        }),
        ('Важные даты', {
            'fields': (
                ("date_joined",),
                ('last_login',)
            ),
        }),
    )
    readonly_fields = ('password',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id', 'username', 'first_name', 'last_name',
        'language_code', 'deep_link',
        'created_at', 'updated_at', "is_blocked_bot",
    ]
    list_filter = ["is_blocked_bot", ]
    search_fields = ('username', 'user_id')
    fieldsets = (
        ('Основное', {
            'fields': (
                ("user_id",),
                ('username', 'language_code'),
                ('first_name', 'last_name'),
            ),
        }),
        ('Дополнительная информация', {
            'fields': (
                ('deep_link',),
                ("is_blocked_bot",),
                ('is_admin',),
            ),
        }),
        ('Важные даты', {
            'fields': (
                ('created_at',),
                ('updated_at',)
            ),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def make_group(self, request, queryset):
        user_ids = queryset.values_list('user_id', flat=True)
        if 'apply' in request.POST:
            group = forms.MakeGroupForm(request.POST).save()
            url = reverse(f'admin:{group._meta.app_label}_{group._meta.model_name}_changelist')#, args=[group.id])
            return HttpResponseRedirect(url)

        else:
            form = forms.MakeGroupForm(initial={'_selected_action': user_ids, 'users': user_ids})
            return render(
                request, "admin/make_group.html", {
                    'form': form, 'title': u'Создание новой группы'}
            )

    def broadcast(self, request, queryset):
        """ Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        # user_ids = queryset.values_list('user_id', flat=True).distinct().iterator()
        user_ids = queryset.values_list('user_id', flat=True)

        if 'apply' in request.POST:
            #broadcast_message_text = request.POST["broadcast_text"]
            f = forms.BroadcastForm(request.POST, request.FILES)
            if f.is_valid():
                broadcast = f.save()
            
            if DEBUG:  # for test / debug purposes - run in same thread
                # for user_id in user_ids:
                #     _send_message(user_id=user_id, text=broadcast_message_text)

                self.message_user(request, f"Рассылка {len(queryset)} сообщений начата")

            else:
                #broadcast_message.delay(text=broadcast_message_text, user_ids=list(user_ids))
                pass
                
            url = reverse(f'admin:{broadcast._meta.app_label}_{broadcast._meta.model_name}_changelist')
            return HttpResponseRedirect(url)
        else:
            form = forms.BroadcastForm(initial={'_selected_action': user_ids, 'users': user_ids})
            return render(
                request, "admin/broadcast_message.html", {
                    'form': form, 
                    'title': u'Создание рассылки сообщений'
                }
            )
    actions = [broadcast, make_group]
    broadcast.short_description = 'Создать рассылку'
    make_group.short_description = 'Создать группу'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'message_type', 'clicks', 'group', 'updated_at', 'created_at'
    ]
    list_filter = ["message_type", "group"]
    search_fields = ('name', 'user_id')
    fieldsets = (
        ('Основное', {
            'fields': (
                ("name",),
                ('text',),
                ('message_type',),
                ('clicks',)
            ),
        }),
        ('Ограничения', {
            'fields': (
                ('messages',),
                ("group",),

            ),
        }),
        ('Медия', {
            'fields': (
                ("files",),
            ),
        }),
        ('Важные даты', {
            'fields': (
                ('created_at',),
                ('updated_at',)
            ),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('messages', 'files')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'created_at'
    ]
    search_fields = ('name',)
    fieldsets = (
        ('Основное', {
            'fields': (
                ("name",),
            ),
        }),
        ('Пользователи', {
            'fields': (
                ("users",),
            ),
        }),
        ('Важные даты', {
            'fields': (
                ('created_at',)
            ),
        }),
    )
    filter_horizontal = ('users',)
    readonly_fields = ('created_at',)


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'created_at'
    ]
    search_fields = ('name', 'tg_id')
    fieldsets = (
        ('Основное', {
            'fields': (
                ("name",),
                ("message",),
            ),
        }),
        ('Пользователи и группы', {
            'fields': (
                ("users",),
                ('group',),
            ),
        }),
        ('Важные даты', {
            'fields': (
                ('created_at',)
            ),
        }),
    )
    filter_horizontal = ('users',)
    readonly_fields = ('created_at',)

    def send_mailing(self, request, queryset):
        group_ids = queryset.values_list('group_id', flat=True)
        self.message_user(
            request, f"Рассылка {len(queryset)} сообщений начата!")

    actions = [send_mailing]
    send_mailing.short_description = 'Начать рассылку'


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'tg_id', 'file', 'created_at'
    ]
    search_fields = ('name', 'tg_id')
    fieldsets = (
        ('Основное', {
            'fields': (
                ("name",),
                ("tg_id",),
            ),
        }),
        ('Информация о файле', {
            'fields': (
                ("file"),
                ('created_at',),
            ),
        })
    )
    readonly_fields = ('created_at',)
