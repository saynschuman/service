from datetime import timedelta

from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from six import text_type
from rest_framework.exceptions import ValidationError

from backend.users.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Статус пользователя, для токена
        token['status'] = user.user_status
        token['status_display'] = user.get_user_status_display()

        return token

    def validate(self, attrs):
        try:
            User.objects.get(username=attrs[self.username_field])
        except User.DoesNotExist:
            raise ValidationError('login_failed', 0)

        data = super(TokenObtainPairSerializer, self).validate(attrs)



        # if self.user.user_status == User.STATUS_CLIENT:
        #     try:
        #         end_course = self.user.end_course + timedelta(days=90)
        #     except TypeError:
        #         raise serializers.ValidationError(
        #             _('No end date for course'),
        #         )
        #     else:
        #         if now().date() > end_course:
        #             raise serializers.ValidationError(
        #                 _('Your account has expired'),
        #             )

        refresh = self.get_token(self.user)

        data['refresh'] = text_type(refresh)
        data['access'] = text_type(refresh.access_token)

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Получение токена доступа
    """
    serializer_class = CustomTokenObtainPairSerializer
