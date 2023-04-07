from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from solo.admin import SingletonModelAdmin
from .models import User, Company, UserActivity, UsersSettings, UserDayActivity


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    list_display = ('username', 'email', 'company', 'user_status', 'is_active', 'start_course', 'end_course')
    list_editable = ('is_active',)
    list_filter = ('user_status', 'is_active', 'company')
    fieldsets = UserAdmin.fieldsets + (
        ('Профиль', {'fields': ('design', 'user_status', 'company', 'curator_company', 'created', 'updated')}),
        ('Временные ограничения', {'fields': ('start_course', 'end_course', 'time_limitation')}),
        ('Чаты', {'fields': ('teacher_chat', 'group_chat', 'tech_chat')}),
    )
    readonly_fields = ['created', 'updated']
    search_fields = ['username', 'email']

    actions = ['on_tag', 'off_tag']

    def on_tag(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, 'Выбранные объекты включены')

    def off_tag(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, 'Выбранные объекты выключены')

    on_tag.short_description = 'Включить'
    off_tag.short_description = 'Выключить'


admin.site.register(User, MyUserAdmin)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'updated')
    search_fields = ['title']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'headers', 'payload', 'total_time', 'created', 'updated')
    search_fields = ['user__username']


@admin.register(UserDayActivity)
class UserDayActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'course_id', 'day', 'human_time', 'seconds', 'created', 'updated')
    search_fields = ('user__username',)
    list_filter = ('day', 'course_id')
    raw_id_fields = ('user',)


@admin.register(UsersSettings)
class UsersSettingsAdmin(SingletonModelAdmin):
    list_display = ('user_field_separator', 'users_separator')
