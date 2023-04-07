import time
from datetime import timedelta, time

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.db.models import Count, Q, DateTimeField, Max, IntegerField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from solo.models import SingletonModel

from backend.helpers import BaseModel


class CompanyQuerySet(models.QuerySet):

    def with_prefetch_related(self):
        return self.prefetch_related('company_users')

    def with_annotations(self):
        return self.annotate(
            active_users=Count(
                'company_users',
                filter=Q(company_users__is_active=True, company_users__user_status=User.STATUS_CLIENT),
            ),
            all_users=Count(
                'company_users',
                filter=Q(company_users__user_status=User.STATUS_CLIENT),
            )
        )


class Company(BaseModel):
    title = models.CharField('Название', max_length=255, unique=True)

    objects = CompanyQuerySet.as_manager()

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        ordering = ['title', '-created']

    def __str__(self):
        return self.title


class UserManager(BaseUserManager):
    """Extended manager for User model."""

    use_in_migrations = False


class UserQuerySet(models.QuerySet):
    """Extended queryset for User model."""

    def with_prefetch_related(self):
        return self.prefetch_related('courses', 'curator_company', 'passings')

    def with_select_related(self):
        return self.select_related('company')

    def with_base_related(self):
        """Return QuerySet with base related."""
        return self.select_related(
            'company',
        )

    def with_extend_related(self):
        """Return QuerySet with extend related."""
        return self.with_base_related().prefetch_related(
            'days_activity',
            'material_passings',
            'passings',
            'attempts',
        )

    def for_curator(self, companies):
        """Return QuerySet for curator"""
        return self.filter(
            is_active=True,
            company__in=companies,
            courses__isnull=False,
        )

    def with_annotations(self):
        """
        last_activity
        """

        return self.annotate(
            last_activity=Max('days_activity__created', output_field=DateTimeField()),
        )

    def with_passing_on_check(self):
        """
        аннотируестя кол-во прохождений на проверке
        """
        return self.annotate(
            on_check=Count(
                'passings',
                filter=Q(
                    passings__success_passed=1,
                    passings__is_trial=False,
                    # passings__finish_time__is_null=False,
                ),
                output_field=IntegerField()),
            last_passing_dt=Max(
                'passings__finish_time',
                filter=Q(
                    passings__task__is_final=True, # uncomment if you need final tasks only
                    passings__success_passed=0,
                    passings__is_trial=False,
                    passings__finish_time__isnull=False,
                ),
                output_field=DateTimeField()),
        )
    def with_last_passing_date(self):
        """
        аннотируестя дата последнего прохождения финального теста
        """
        # отфильтровать нулевые значения
        return self.annotate(
            last_passing_dt=Max(
                'passings__finish_time',
                filter=Q(
                    passings__task__is_final=True,
                    passings__success_passed=0,
                    passings__is_trial=False,
                    passings__finish_time__isnull=False
                ),
                output_field=DateTimeField()),
        )


class User(AbstractUser, BaseModel):
    # Статусы пользователей
    STATUS_ADMIN = 0
    STATUS_MODERATOR = 1
    STATUS_CLIENT = 2
    STATUS_CURATOR = 3

    STATUS_CHOICES = (
        (STATUS_ADMIN, 'Администратор'),
        (STATUS_MODERATOR, 'Модератор'),
        (STATUS_CLIENT, 'Клиент'),
        (STATUS_CURATOR, 'Куратор'),
    )

    # Дизайны интерфейса
    DEFAULT_DESIGN = 0
    INTELL_DESIGN = 1

    DESIGN_CHOICES = (
        (DEFAULT_DESIGN, 'Дефолтный дизайн'),
        (INTELL_DESIGN, 'Интеллека дизайн'),
    )

    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    description = models.TextField('Примечание', blank=True, null=True)
    design = models.SmallIntegerField('Дизайн интерфейса', choices=DESIGN_CHOICES, default=DEFAULT_DESIGN)
    user_status = models.SmallIntegerField('Статус пользователя', choices=STATUS_CHOICES, default=STATUS_CLIENT)
    time_limitation = models.DateTimeField('Время ограничения доступа', blank=True, null=True)
    company = models.ForeignKey(
        Company,
        verbose_name='Компания',
        related_name='company_users',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    curator_company = models.ManyToManyField(
        Company,
        verbose_name='Курируемые компании',
        blank=True,
        related_name='curator_company'
    )
    start_course = models.DateField('Время начала курса', blank=True, null=True)
    end_course = models.DateField('Время окончания курса', blank=True, null=True)

    old_password = models.CharField('Пароль клиента', max_length=100, blank=True, null=True)

    # Права на чаты
    teacher_chat = models.BooleanField('Чат с преподавателем', default=False)
    group_chat = models.BooleanField('Чат с одногрупниками', default=False)
    tech_chat = models.BooleanField('Чат с тех. поддержкой', default=True)

    # Доступность вебинаров
    webinars = models.BooleanField('Доступность вебинаров', default=False)

    # Last user activity
    last_active = models.DateTimeField('Последняя активность', blank=True, null=True)

    objects = UserManager.from_queryset(UserQuerySet)()

    @classmethod
    def get_online_clients_count(cls, timedelta_min):
        return cls.objects.filter(
            user_status=cls.STATUS_CLIENT,
            last_active__range=(
                timezone.now() - timedelta(minutes=timedelta_min),
                timezone.now()
            )
        ).count()

    @classmethod
    def get_online_clients_day_count(cls, day_date):
        return cls.objects.filter(
            user_status=cls.STATUS_CLIENT,
            last_active__range=(
                day_date,
                day_date + timedelta(days=1)
            )
        ).count()

    @property
    def is_admin(self):
        return self.user_status == self.STATUS_ADMIN

    @property
    def is_moderator(self):
        return self.user_status == self.STATUS_MODERATOR

    @property
    def is_client(self):
        return self.user_status == self.STATUS_CLIENT

    @property
    def company_title(self):
        return self.company.title

    @property
    def user_course(self):
        course = self.courses.first()
        return self.courses.first().id if course else None

    @property
    def active_courses(self):
        return self.courses.filter(is_active=True)


class UserOnlineHistory(BaseModel):
    date = models.DateField('Дата', default=timezone.now, unique=True)
    active_clients_count = models.PositiveIntegerField('Кол-во активных клиентов', default=0)

    class Meta:
        verbose_name = 'История активных клиентов'
        verbose_name_plural = 'История активных клиентов'
        ordering = ['date']

    def __str__(self):
        return f'{self.active_clients_count} активных клиентов за {self.date}'


class UserActivity(BaseModel):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='activities', on_delete=models.CASCADE)
    headers = models.TextField('headers', blank=True)
    payload = models.TextField('payload', blank=True, null=True)
    course_id = models.IntegerField(
        'ID курса в момент посещения',
        blank=True,
        null=True,
    )

    # course = models.PositiveSmallIntegerField('ID курса', blank=True, null=True)
    # material = models.PositiveSmallIntegerField('ID материала', blank=True, null=True)
    # test = models.PositiveSmallIntegerField('ID материала', blank=True, null=True)

    class Meta:
        verbose_name = 'Пользовательская активность'
        verbose_name_plural = 'Пользовательская активность'

    def __str__(self):
        return f'Активность пользователя ID_{self.user.id}'

    @property
    def total_time(self):
        return self.updated - self.created


class UserDayActivityQuerySet(models.QuerySet):
    """Extended queryset for UserDayActivity model."""

    def with_select_related(self):
        return self.select_related('user')

    def for_curator(self, companies):
        """Return QuerySet for curator"""
        return self.with_select_related().filter(
            user__is_active=True,
            user__company__in=companies,
            user__courses__isnull=False,
        )


class UserDayActivity(BaseModel):
    """
    Время активности пользователей по дням
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='days_activity',
        on_delete=models.CASCADE,
    )
    day = models.DateField(
        'Дата',
        auto_now_add=True,
    )
    seconds = models.PositiveSmallIntegerField(
        'Секунды',
        default=0,
    )
    course_id = models.SmallIntegerField(
        'ID курса в момент посещения',
        blank=True,
        null=True,
    )

    objects = UserDayActivityQuerySet.as_manager()

    class Meta:
        verbose_name = 'Время активности пользователей по дням'
        verbose_name_plural = 'Время активности пользователей по дням'
        unique_together = ('user', 'day')

    def __str__(self):
        return f'Активность пользователя ID_{self.user.id} на {self.day}'

    @property
    def human_time(self):
        return time.strftime("%H:%M:%S", time.gmtime(self.seconds))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.user:
            from backend.courses.models import Course
            course = Course.objects.filter(users=self.user).first()
            self.course = course.id
        super().save(force_insert, force_update, using, update_fields)


class UsersSettings(SingletonModel):
    """
    Различные настройки
    """

    user_field_separator = models.CharField('Рзаделитель полей для пользователя', max_length=3)
    users_separator = models.CharField('Рзаделитель пользователей', max_length=3)

    class Meta:
        verbose_name = 'Различные настройки'
        verbose_name_plural = 'Различные настройки'

    def __str__(self):
        return f'{self.user_field_separator}, {self.users_separator}'


class UserEnterStatistic(BaseModel):
    payload = models.TextField('payload', blank=True, null=True)

class UserLogErrors(BaseModel):
    """
    Логирование ошибок для статистики
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='user_log_errors',
        on_delete=models.CASCADE,
    )
    text = models.TextField("Текст ошибки", blank=True, null=True)

    class Meta:
        verbose_name = 'User Log Errors'
        verbose_name_plural = 'User Log Errors'
        ordering = ['-created']
        db_table = 'user_log_errors'

    def __str__(self):
        return f'Ошибка пользователя {self.user}, создана {self.created}, текст: {self.text}'
