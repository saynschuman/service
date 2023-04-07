from rest_framework import generics
from backend.notifications.models import MessageNotification
from backend.notifications.serializers import MessageNotificationSerializer
from rest_framework import permissions

class MessageNotificationView(generics.ListCreateAPIView):
    queryset = MessageNotification.objects.all()
    serializer_class = MessageNotificationSerializer
    permission_classes = (permissions.IsAuthenticated, )


class MessageNotificationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageNotificationSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = MessageNotification.objects.all()
