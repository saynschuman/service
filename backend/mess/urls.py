from django.urls import path

from .views import (
    EmptyChatView,
    SupportChatView,
    SupportNavView,
    ItemChatView,
    TeacherChatView,
    TeacherNavView,
    GroupChatView,
)

app_name = 'chat'

urlpatterns = [
    path('', EmptyChatView.as_view(), name='empty'),
    path('support_chat/', SupportChatView.as_view(), name='support'),
    path('teacher_chat/', TeacherChatView.as_view(), name='teacher'),
    path('group_chat/', GroupChatView.as_view(), name='group'),
    path('s_chats/', SupportNavView.as_view(), name='s_chats'),
    path('t_chats/', TeacherNavView.as_view(), name='t_chats'),
    path('<int:pk>/', ItemChatView.as_view(), name='chat_detail'),
]
