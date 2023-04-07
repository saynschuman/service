from django.core.validators import MaxLengthValidator, FileExtensionValidator
from django.db import models
from django.db.models import Max
from django.urls import reverse
from solo.models import SingletonModel

from backend.courses.models import Course
from backend.helpers import BaseModel
from backend.users.models import User, Company


class ChatQuerySet(models.QuerySet):

    def with_prefetch_related(self):
        return self.prefetch_related('users', 'messages')

    def with_annotations(self):
        """
        Время последнего сообщения
        """
        return self.annotate(
            last_message_date=Max('messages__created')
        )


class Chat(BaseModel):
    STATUS_SUPPORT = 0
    STATUS_TEACHER = 1
    STATUS_GROUP = 2

    STATUS_CHOICES = (
        (STATUS_SUPPORT, 'Чат с тех. поддержкой'),
        (STATUS_TEACHER, 'Чат с преподавателем'),
        (STATUS_GROUP, 'Чат с одногруппниками'),
    )
    chat_status = models.SmallIntegerField('Тип чата', choices=STATUS_CHOICES, default=STATUS_SUPPORT)
    users = models.ManyToManyField(User, verbose_name='Пользователи', related_name='user_chats')
    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        related_name='course_chats',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    company = models.ForeignKey(
        Company,
        verbose_name='Компания',
        related_name='company_chats',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    objects = ChatQuerySet.as_manager()

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f'Чат id-{self.pk}'

    def get_absolute_url(self):
        return reverse('chat:chat_detail', kwargs={'pk': self.pk})

    @property
    def is_support(self):
        return self.chat_status == self.STATUS_SUPPORT

    @property
    def is_teacher(self):
        return self.chat_status == self.STATUS_TEACHER

    @property
    def is_group(self):
        return self.chat_status == self.STATUS_GROUP

    @property
    def num_messages(self):
        return self.messages.count()


class Message(BaseModel):
    mess = models.TextField('Сообщение', blank=True, null=True)
    chat = models.ForeignKey(Chat, verbose_name='Чат', related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Отправитель', related_name='messages', on_delete=models.CASCADE)
    image = models.ImageField(
        'Изображение',
        upload_to='chat_images/',
        blank=True,
        null=True,
        validators=[
            MaxLengthValidator(1 * 1024 * 1024),
            FileExtensionValidator(allowed_extensions=('png', 'jpeg', 'jpg', 'bmp')),
        ],
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'Сообщение в чат id-{self.chat.pk} от {self.user.username}'


class UserMessage(BaseModel):
    user = models.ForeignKey(
        User,
        verbose_name='Получатель',
        related_name='user_messages',
        on_delete=models.CASCADE,
    )
    author = models.CharField(max_length=100, default=False, null=True)
    author_id = models.IntegerField(default=False, null=True)
    chat_status = models.IntegerField(default=False, null=True)
    message = models.ForeignKey(
        Message,
        verbose_name='Сообщение',
        related_name='user_messages',
        on_delete=models.CASCADE,
    )
    message_text=models.TextField(default="")
    is_read = models.BooleanField('Прочтено', default=False)

    class Meta:
        verbose_name = 'Сообщение пользователю'
        verbose_name_plural = 'Сообщения пользователей'
        unique_together = ('user', 'message')

    def __str__(self):
        is_read = 'ПРОЧТЕНО' if self.is_read else 'НЕ ПРОЧТЕНО'
        return f'Сообщение ID:{self.message_id} для пользователя ID:{self.user_id} {is_read}'


class FirebaseSettings(SingletonModel):
    updated = models.DateTimeField('Время изменения', auto_now=True)
    apikey = models.CharField('api key', max_length=255)

    class Meta:
        verbose_name = 'Настройки хранилища чатов'
        verbose_name_plural = 'Настройки хранилища чатов'

    def __str__(self):
        return self.apikey
