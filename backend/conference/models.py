from django.db import models
from solo.models import SingletonModel


class ConferenceSettings(SingletonModel):
    updated = models.DateTimeField('Время изменения', auto_now=True)
    apikey = models.CharField('api key', max_length=255)

    class Meta:
        verbose_name = 'Настройки конференций'
        verbose_name_plural = 'Настройки конференций'

    def __str__(self):
        return self.apikey
