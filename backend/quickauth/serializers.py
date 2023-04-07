from rest_framework import serializers
from backend.quickauth.models import QuickLogin

class QuickLoginSerializer(serializers.ModelSerializer):
  class Meta:
      model = QuickLogin
      fields = (
        'client_login',
        'curator_login',
        'moderator_login',
        'admin_login',
        'client_password',
        'curator_password',
        'moderator_password',
        'admin_password',
      )
