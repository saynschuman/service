from django.db import models
from django.http import HttpResponse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken


class BaseModel(models.Model):
    """
    База для всех моделей
    """
    created = models.DateTimeField('Время создания', auto_now_add=True)
    updated = models.DateTimeField('Время изменения', auto_now=True)

    class Meta:
        abstract = True


def is_allowed(request):
    status = 403

    auth_token = request.COOKIES.get('access')
    if auth_token:
        try:
            obj = AccessToken(auth_token)
            obj.verify()
        except TokenError:
            pass
        else:
            status = 200

    return HttpResponse(status=status)
