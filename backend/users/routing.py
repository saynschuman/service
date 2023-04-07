from django.urls import path

from .consumers import UserActivityConsumer, OnlineUsersConsumer

websocket_urlpatterns = [
    path('ws/user_activity/', UserActivityConsumer),
    path('ws/online_users/', OnlineUsersConsumer)
]
