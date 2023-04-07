from django.db import models
from solo.models import SingletonModel


class EmailSettings(SingletonModel):
    """
    Глобальные настройки почты
    """

    email = models.EmailField('E-mail', max_length=255)
    password = models.CharField('Пароль', max_length=255)
    port = models.PositiveSmallIntegerField('Порт', default=587)
    tls = models.BooleanField('Использовать TLS', default=True)
    host = models.CharField('Хост провайдера', max_length=255)

    class Meta:
        verbose_name = 'Глобальные настройки почты'

    def __str__(self):
        return self.email


class EmailLogger(models.Model):
    """
    Логи ошибок
    """

    message = models.TextField('Сообщение')
    created = models.DateTimeField('Время создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Лог ошибок'
        verbose_name_plural = 'Логи ошибок'
        ordering = ['-created']

    def __str__(self):
        return str(self.id)
