from django.contrib import admin

from .models import UserAnswer, Attempts


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('passing', 'question', 'verifier', 'created', 'updated')
    list_filter = ('created',)
    raw_id_fields = ('passing', 'question', 'answer', 'answers', 'verifier')


@admin.register(Attempts)
class AttemptsAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'num_attempts', 'created', 'updated')
    search_fields = ['user', 'course']
    list_filter = ('created',)
