from rest_framework import serializers
from backend.notifications.models import MessageNotification

class MessageNotificationSerializer(serializers.ModelSerializer):
  class Meta:
      model = MessageNotification
      fields = (
        'id',
        'text',
        'author',
      )
