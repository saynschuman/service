from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Chat, Message, FirebaseSettings, UserMessage


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'chat_status', 'course', 'company', 'created')
    list_filter = ('created', 'company', 'chat_status')
    raw_id_fields = ('course', 'company')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'user', 'mess', 'created', 'updated')
    list_filter = ('created', 'updated')
    raw_id_fields = ('chat', 'user')


@admin.register(FirebaseSettings)
class UsersSettingsAdmin(SingletonModelAdmin):
    list_display = ('apikey', 'updated')


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'message', 'is_read', 'created', 'updated')
    list_filter = ('is_read',)
    raw_id_fields = ('user', 'message')
