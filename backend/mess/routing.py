from django.urls import path

from backend.mess.consumers import GroupChatConsumer, TeacherChatConsumer, SupportChatConsumer

websocket_urlpatterns = [
    path('ws/group_chat/<int:user_id>/<str:token>/', GroupChatConsumer),
    path('ws/teacher_chat/<int:user_id>/<str:token>/', TeacherChatConsumer),
    path('ws/support_chat/<int:user_id>/<str:token>/', SupportChatConsumer),

    path('ws/g_chat/<int:user_id>/<str:token>/<int:chat_id>/', GroupChatConsumer),
    path('ws/t_chat/<int:user_id>/<str:token>/<int:chat_id>/', TeacherChatConsumer),
    path('ws/s_chat/<int:user_id>/<str:token>/<int:chat_id>/', SupportChatConsumer),
]
