from django.urls import path

from backend.notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/notifications/<int:user_id>', NotificationConsumer),
]
