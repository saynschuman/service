from django.contrib import admin

from .models import (
    Course,
    Tag,
    Material,
    Task,
    Question,
    Answer,
    MaterialPassing,
    Passing,
    Bookmark,
    IssuedTask,
    UserCourseSettings
)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'material', 'title', 'page', 'created', 'updated')
    list_filter = ('created', 'updated')


@admin.register(MaterialPassing)
class MaterialPassingAdmin(admin.ModelAdmin):
    list_display = ('user', 'material', 'status', 'created', 'updated')
    list_filter = ('created', 'updated', 'status')


@admin.register(Passing)
class PassingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'task',
        'start_time',
        'finish_time',
        'out_of_time',
        'success_passed',
        'user_points',
        'max_points',
    )
    list_filter = ('created', 'success_passed')
    search_fields = ('user__username',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'created', 'updated')
    search_fields = ['created']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'is_active',
        'registered_num',
        'created',
        'updated',
    )
    search_fields = ['title', 'author__username']
    list_filter = ('is_active', 'created')

    actions = ['on_tag', 'off_tag']

    def on_tag(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, 'Выбранные объекты включены')

    def off_tag(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, 'Выбранные объекты выключены')

    on_tag.short_description = 'Включить'
    off_tag.short_description = 'Выключить'


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    raw_id_fields = ('original_link',)
    search_fields = ['course__title', ]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'passing',
        'attempts',
        'is_necessarily',
        'is_chance',
        'is_mix',
        'is_miss',
        'is_final',
        'is_hidden',
        'created',
        'updated',
        'num_questions',
        'rank',
    )
    raw_id_fields = ['material']
    search_fields = ['title', 'material__course__title']
    list_filter = (
        'is_necessarily',
        'is_chance',
        'is_mix',
        'is_miss',
        'is_final',
        'is_hidden',
        'created',
        'is_active',
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'm_file', 'is_free_answer', 'score', 'created', 'updated')
    search_fields = ['text']
    list_filter = ('is_free_answer', 'created')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'rank', 'is_true', 'created', 'updated')
    search_fields = ['text']
    list_filter = ('is_true', 'created')

@admin.register(IssuedTask)
class IssuedTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'issued_date_time',)
    search_fields = ['text']
    list_filter = ('task', 'user')


@admin.register(UserCourseSettings)
class UserCourseSettingsAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'start_course', 'end_course')
    list_filter = ('course', 'user')
