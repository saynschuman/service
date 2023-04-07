from django.contrib import admin
from solo.admin import SingletonModelAdmin

from backend.conference.models import ConferenceSettings


@admin.register(ConferenceSettings)
class UsersSettingsAdmin(SingletonModelAdmin):
    list_display = ('apikey', 'updated')
