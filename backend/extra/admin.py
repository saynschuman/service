from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import EmailLogger, EmailSettings


@admin.register(EmailLogger)
class EmailLoggerAdmin(admin.ModelAdmin):
    list_display = ('created', 'message')
    readonly_fields = ('created', 'message')
    list_filter = ('created',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EmailSettings)
class EmailSettingsAdmin(SingletonModelAdmin):
    list_display = ('email',)
