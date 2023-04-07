import datetime

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, OuterRef, Subquery, IntegerField, Q
from django.utils.timezone import now
from django.core.files.base import ContentFile
from upload_validator import FileTypeValidator
from django.core.validators import MaxValueValidator, MinValueValidator

from backend.helpers import BaseModel
from backend.users.models import User
from backend.utils.methods import path_and_rename
from datetime import timedelta


class Tag(BaseModel):
    tag = models.CharField('Тэг', max_length=50)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['tag', '-created']

    def __str__(self):
        return self.tag


class CourseQuerySet(models.QuerySet):

    def with_prefetch_related(self):
        return self.prefetch_related('users', 'moderators', 'tag')

    def with_tasks_prefetch(self):
        return self.prefetch_related('materials', 'materials__tasks')

    def with_select_related(self):
        return self.select_related('author')

    def with_annotations(self):
        """
        Кол-во заходивших на сайт
        Кол-во успешно закончивших курс
        """
        users = User.objects.filter(
            courses=OuterRef('pk'),
            days_activity__isnull=False,
            days_activity__course_id=OuterRef('pk')
        ).values('courses')
        count_users = users.annotate(c=Count('pk', distinct=True)).values('c')

        completed = User.objects.prefetch_related(
            'passings',
        ).filter(
            courses=OuterRef('pk'),
            passings__success_passed=Passing.PASSED,
            passings__task__material__course=OuterRef('pk'),
            passings__task__material__is_active=True,
            passings__task__is_final=True,
        ).values('courses')
        completed_users = completed.annotate(
            c=Count('pk', distinct=True)
        ).values('c')

        return self.annotate(
            visit_num=Subquery(count_users, output_field=IntegerField()),
            completed_num=Subquery(
                completed_users,
                output_field=IntegerField()
            ),
        )

    def with_num_intermediate_tests(self):
        """
        аннотируется кол-во промежуточных тестов в курсе
        -> tasks
            is_active=True
            is_final=False
        -> material
            is_active=True
        """
        return self.with_tasks_prefetch().annotate(
            num_intermediate_tests=Count(
                'materials__tasks',
                filter=Q(
                    materials__is_active=True,
                    materials__tasks__is_active=True,
                    materials__tasks__is_final=False,
                ),
                output_field=IntegerField()),
        )


class Course(BaseModel):
    title = models.CharField('Название курса', max_length=255, unique=True)
    description = models.TextField('Описание', blank=True, null=True)
    teacher = models.TextField(
        'Текстовое представление преподавателя',
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор курса',
        related_name='author_courses',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    moderators = models.ManyToManyField(
        User,
        verbose_name='Модераторы курса',
        related_name='moderator_courses',
        blank=True,
    )
    is_active = models.BooleanField('Активно', default=True)

    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='courses',
        blank=True,
    )
    users = models.ManyToManyField(
        User,
        verbose_name='Пользователи',
        related_name='courses',
        blank=True,
    )
    start_course = models.DateField('Время начала курса', blank=True, null=True)
    end_course = models.DateField('Время окончания курса', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    t_chat = models.BooleanField('Чат с преподавателем', default=False)
    s_chat = models.BooleanField('Чат с одногрупниками', default=False)
    g_chat = models.BooleanField('Чат с тех. поддержкой', default=True)

    objects = CourseQuerySet.as_manager()

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created', 'title']

    def __str__(self):
        return self.title

    def get_all_tasks(self):
        return Task.objects.filter(material__course=self)

    def get_success_tasks_for_user(self, user):
        return self.get_all_tasks().filter(
            task_passings__user=user,
            task_passings__success_passed=Passing.PASSED,
        )

    def get_all_materials(self):
        return Material.objects.filter(course=self)

    def get_passed_materials_for_user(self, user):
        return self.get_all_materials().filter(
            material_passings__user=user,
            material_passings__status=MaterialPassing.STATUS_PASSED,
        )

    @property
    def registered_num(self):
        """
        Кол-во зарегистрировавшихся на курс
        """
        return self.users.count()

    def delete(self, using=None, keep_parents=False):

        # Удаляем теги, если к ним больше не привязан ни один курс
        for tag in self.tag.all():
            if tag.courses.count() == 1:
                tag.delete()

        return super().delete(using, keep_parents)


class Material(BaseModel):
    """
    Материалы для курса
    """
    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        related_name='materials',
        on_delete=models.CASCADE
    )
    title = models.CharField('Название материала', max_length=400)
    text = models.TextField('Текстовый контент', blank=True, null=True)
    video = models.FileField(
        'Видео контент',
        max_length=500,
        upload_to=path_and_rename,
        null=True,
        blank=True,
    )
    pdf = models.FileField(
        'PDF контент',
        max_length=500,
        upload_to=path_and_rename,
        null=True,
        blank=True,
        validators=[FileTypeValidator(
            allowed_extensions=['.pdf'],
            allowed_types=['application/pdf']
        )],
    )
    is_active = models.BooleanField('Активно', default=True)
    is_download = models.BooleanField('Разрешено скачивать', default=False)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        verbose_name='Родительский материал',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    rank = models.PositiveSmallIntegerField('Очереднось показа', default=0)
    original_link = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    video_link = models.URLField('Ссылка на видео', blank=True, null=True)

    class Meta:
        verbose_name = 'Материалы курса'
        verbose_name_plural = 'Материалы курсов'
        ordering = ['rank', 'title', '-created']

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return f'id:{self.pk} {self.title} >>>> {self.parent.pk if self.parent else None}'

    def copy_files_from_material(self, material_id):
        material = Material.objects.get(id=material_id)
        if bool(material.video):
            new_video = ContentFile(material.video.read())
            original_video_name = material.video.name.split("/")[-1]
            new_video_name = f"{self.pk}_{original_video_name}"
            self.video.save(new_video_name, new_video)
        if bool(material.pdf):
            new_pdf = ContentFile(material.pdf.read())
            original_pdf_name = material.pdf.name.split("/")[-1]
            new_pdf_name = f"{self.pk}_{original_pdf_name}"
            self.pdf.save(new_pdf_name, new_pdf)
        self.save()

    @property
    def original_data(self):
        result = {}
        if self.original_link.text:
            result['text'] = self.original_link.text
        if self.original_link.pdf:
            result['pdf'] = self.original_link.pdf.url
        if self.original_link.video:
            result['video'] = self.original_link.video.url

        return result

    # def clean(self):
    #     if not self.text and not self.video and not self.pdf:
    #         raise ValidationError('Одно из этих полей должно быть заполнено: text, video, pdf')
    #     super().clean()


class TaskQuerySet(models.QuerySet):

    def with_prefetch_related(self):
        return self.prefetch_related('questions')

    def with_select_related(self):
        return self.select_related('material')


class Task(BaseModel):
    """
    Задание-тесты для материала курса
    """
    material = models.ForeignKey(
        Material,
        verbose_name='Материал',
        related_name='tasks',
        on_delete=models.CASCADE
    )
    title = models.CharField('Название задания', max_length=255)
    description = models.TextField('Описание', blank=True, null=True)
    text_explanation = models.TextField(
        'Описание с хэштегами',
        blank=True,
        null=True
    )
    travel_time = models.TimeField('Время проохождения')
    retake_seconds = models.PositiveIntegerField(
        'Интервала пересдачи',
        default='0'
    )
    passing = models.SmallIntegerField(
        'Процент ответов для прохождения',
        default=100,
        validators=[MinValueValidator(1)],
    )
    attempts = models.SmallIntegerField(
        'Кол-во попыток',
        default=100,
        validators=[MinValueValidator(1)],
    )
    is_necessarily = models.BooleanField(
        'Обязательно для прохождения',
        default=True
    )
    is_chance = models.BooleanField('Случайный вабор вопросов', default=True)
    is_mix = models.BooleanField('Перемешать ответы', default=True)
    is_miss = models.BooleanField('Пропускать вопросы', default=False)
    is_final = models.BooleanField('Итоговое тестирование', default=False)
    is_hidden = models.BooleanField('Скрывать результаты', default=False)
    rank = models.PositiveSmallIntegerField('Очереднось показа', default=0)
    is_active = models.BooleanField('Активно', default=True)
    trial_attempts = models.PositiveSmallIntegerField(
        'Кол-во пробных попыток',
        default=0
    )
    trial_percents = models.PositiveSmallIntegerField(
        'Процент пробных попыток',
        default=50,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )
    max_attempts_to_pass = models.PositiveSmallIntegerField(
        'Максимальное кол-во сдач',
        default=3
    )

    objects = TaskQuerySet.as_manager()

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['rank', 'title', '-created']

    def __str__(self):
        return self.title

    @property
    def num_questions(self):
        return self.questions.all().count()

    def get_questions_score(self):
        """
        Сумма всех балоов за правильные ответы
        """
        return sum(q.score for q in self.questions.all())

    def get_min_passing_score(self):
        """
        Минимальное кол-во баллов для успешности
        """
        return (self.get_questions_score() / 100) * self.passing

    @property
    def prepared_text(self):
        text = self.text_explanation
        if not text:
            return None

        num = '#number#'
        percent = '#question#'
        time = '#time#'

        if num in text:
            text = text.replace(num, str(self.num_questions))

        if percent in text:
            text = text.replace(percent, str(self.passing))

        if time in text:
            text = text.replace(time, str(self.travel_time))

        return text


class Question(BaseModel):
    tasks = models.ManyToManyField(
        Task,
        verbose_name='Задание',
        related_name='questions'
    )
    text = models.TextField('Вопрос')
    m_file = models.FileField(
        'Медиа-файл вопроса',
        upload_to='question_files/',
        null=True,
        blank=True
    )
    is_free_answer = models.BooleanField('Произвольный ответ', default=False)
    score = models.SmallIntegerField(
        'Максимальные баллы за ответ',
        default=1,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created']

    def __str__(self):
        return self.text

    @property
    def variants(self):
        """
        Возможные варианты ответов
        """
        return self.answers.values_list('id', 'text', 'is_true')

    @property
    def correct_answer(self):
        """
        Список id правильных ответов
        """
        return self.answers.filter(is_true=True).values_list('id', flat=True)


class Answer(BaseModel):
    """
    Вариант ответа к вопросу из задания/тестирования
    """

    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        related_name='answers',
        on_delete=models.CASCADE
    )
    is_true = models.BooleanField('Правильный ответ', default=False)
    text = models.TextField('Вариант ответа')
    rank = models.PositiveSmallIntegerField('Очереднось показа', default=0)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-created']

    def __str__(self):
        return self.text


class MaterialPassing(BaseModel):
    """
    Прохождение материала клиентом
    """

    STATUS_NOT_STARTED = 0
    STATUS_STARTED = 1
    STATUS_PASSED = 2

    STATUS_CHOICES = (
        (STATUS_NOT_STARTED, 'Не начато'),
        (STATUS_STARTED, 'Начато'),
        (STATUS_PASSED, 'Пройдено'),
    )

    material = models.ForeignKey(
        Material,
        verbose_name='Материал',
        related_name='material_passings',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='material_passings',
        on_delete=models.CASCADE,
        limit_choices_to={'user_status': User.STATUS_CLIENT},
    )
    status = models.SmallIntegerField(
        'Статус прохождения',
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
    )

    text = models.TextField(blank=True)
    userName = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Прохождение материала'
        verbose_name_plural = 'Прохождение материалов'
        ordering = ['-created']
        # unique_together = ('material', 'user')

    def __str__(self):
        return f'Прохождение материала id_{self.material.pk} пользователем {self.user.username}'


class PassingQuerySet(models.QuerySet):

    def with_prefetch_related(self):
        return self.prefetch_related('user_answers')

    def with_select_related(self):
        return self.select_related('task')


class Passing(BaseModel):
    """
    Прохождение теста пользователем
    """

    # Статусы прохождения
    PASSED = 0
    ON_CHECK = 1
    LIMIT = 2
    ATTEMPTS = 3
    SCORE = 4
    NOT_FINISHED = 5

    PASSED_CHOICES = (
        (PASSED, 'Тест пройден успешно'),
        (ON_CHECK, 'На проверке'),
        (LIMIT, 'Превышено допустимое время прохождения'),
        (ATTEMPTS, 'Превышено допустимое кол-во попыток'),
        (SCORE, 'Процент прохождения не набран'),
        (NOT_FINISHED, 'Не закончен'),
    )

    task = models.ForeignKey(
        Task,
        verbose_name='Задание',
        related_name='task_passings',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='passings',
        on_delete=models.CASCADE
    )
    start_time = models.DateTimeField('Время начала', auto_now_add=True)
    finish_time = models.DateTimeField(
        'Время окончания',
        null=True,
        blank=True
    )
    success_passed = models.PositiveSmallIntegerField(
        'Статус прохождения',
        choices=PASSED_CHOICES,
        default=NOT_FINISHED
    )
    out_of_time = models.BooleanField(
        'Разрешить пересдачу без интервала',
        default=False
    )
    is_trial = models.BooleanField('Пробная попытка', default=False)
    user_points = models.PositiveSmallIntegerField(
        'Баллы за прохождение теста',
        default=0
    )
    max_points = models.PositiveSmallIntegerField(
        'Максимально возможные баллы за тест',
        default=0
    )

    objects = PassingQuerySet.as_manager()

    class Meta:
        verbose_name = 'Прохождение теста'
        verbose_name_plural = 'Прохождения тестов'
        ordering = ['-created']

    def __str__(self):
        return f'Прохождение теста id_{self.task.pk} пользователем {self.user.username}'

    @property
    def travel_time(self):
        if self.start_time and self.finish_time:
            tr_time = self.finish_time - self.start_time
            return timedelta(seconds=tr_time.seconds, days=tr_time.days).total_seconds()

    @property
    def retake_seconds(self):
        previous_passing = Passing.objects.with_select_related().filter(
            task=self.task,
            user=self.user,
        ).order_by('-created').first()

        if previous_passing:
            if not previous_passing.finish_time:
                return None

            past_time = now() - previous_passing.finish_time
            retake_seconds = previous_passing.task.retake_seconds
            retake_timedelta = datetime.timedelta(seconds=retake_seconds)

            if not previous_passing.out_of_time:
                if past_time < retake_timedelta:
                    tt = retake_timedelta - past_time
                    return tt.total_seconds()

        return None

    @property
    def is_final_task(self):
        return self.task.is_final

    @property
    def task_attempts(self):
        return Passing.objects.filter(task=self.task, user=self.user).count()

    @property
    def response_rate(self):
        """
        Процент правильных ответов
        """

        if self.is_trial:
            count = 0
            user_answers = self.user_answers.all().distinct()
            for answer in user_answers:
                if answer.get_user_points() == answer.max_points:
                    count += 1

            answers_count = user_answers.count()
            return f'{count}:{answers_count}'

        try:
            rate = self.user_points / self.max_points * 100
        except ZeroDivisionError:
            # print(
            #     f'ZeroDivisionError: division by zero, {self.max_points}, {self.user_points}')
            return 'Нет данных'
        except TypeError:
            # print(
            #     f'TypeError: unsupported operand type(s) for /: NoneType and int, {self.max_points}, {self.user_points}')
            return 'Нет данных'
        else:
            import math
            return f'{int(math.ceil(rate))}%'

    @property
    def int_response_rate(self):
        """
        Процент правильных ответов
        """

        try:
            rate = self.user_points / self.max_points * 100
        except ZeroDivisionError:
            return None
        except TypeError:
            return None
        else:
            import math
            return int(math.ceil(rate))

    def _get_user_points(self):
        """
        Получение баллов за прохождение тестирования
        :return: int, сумма баллов за ответы
        """
        user_points = 0
        user_answers = self.user_answers.all().distinct()

        for item in user_answers:
            user_points += item.get_user_points()

        return user_points

    def check_free_answer(self):
        user_answer = self.user_answers.filter(
            answer__isnull=True,
            user_points__isnull=True,
            question__is_free_answer=True,
        )
        if user_answer:
            return True

    def check_passing(self, finish=True):
        """
        Рсчитать прохождение теста
        """
        if finish:
            # Устанавливаем время окончания тестирования
            self.finish_time = now()
            self.save(update_fields=['finish_time'])

        # Уложились ли в отведенное время тестирования
        limit = self.task.travel_time.second + self.task.travel_time.minute * \
                60 + self.task.travel_time.hour * 60 * 60
        if self.travel_time and (limit - self.travel_time) < 0:
            self.success_passed = self.LIMIT
            self.save(update_fields=['success_passed'])
            return False

        if self.is_trial:
            self.user_points = self._get_user_points()
            self.save(update_fields=['user_points'])
            return False

        # Кол-во попыток
        current_test_passings = Passing.objects.filter(
            task=self.task,
            user=self.user,
        )
        if current_test_passings.count() > self.task.attempts:
            self.success_passed = self.ATTEMPTS
            self.save(update_fields=['success_passed'])
            return False

        # На проверке у модератора
        on_check = self.check_free_answer()
        if on_check:
            self.success_passed = self.ON_CHECK
            self.save(update_fields=['success_passed'])
            return False

        # Проверка по проценту баллов
        self.user_points = self._get_user_points()
        self.save(update_fields=['user_points'])

        response_rate = self.int_response_rate

        if response_rate and response_rate < self.task.passing:
            self.success_passed = self.SCORE
            self.save(update_fields=['success_passed'])
            return False
        elif response_rate and response_rate >= (self.task.passing - 0.1):
            self.success_passed = self.PASSED
            self.save(update_fields=['success_passed'])
            return True
        else:
            if response_rate == 0:
                self.success_passed = self.SCORE
                self.save(update_fields=['success_passed'])
            return False


class Bookmark(BaseModel):
    """
    Закладка пользователя для материала
    """

    material = models.ForeignKey(
        Material,
        verbose_name='Материал',
        related_name='bookmarks',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='bookmarks',
        on_delete=models.CASCADE,
        limit_choices_to={'user_status': User.STATUS_CLIENT},
    )
    title = models.CharField('Название', max_length=150)
    page = models.PositiveSmallIntegerField('Страница')

    class Meta:
        verbose_name = 'Закладка'
        verbose_name_plural = 'Закладки'
        ordering = ['-created']

    def __str__(self):
        return f'{self.title}, материал: {self.material.title}, стр.: {self.page}'

    @property
    def course(self):
        return self.material.course.id


class IssuedTask(BaseModel):
    task = models.ForeignKey(
        Task,
        verbose_name='Задание',
        related_name='task_issued',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='user_task_issued',
        on_delete=models.CASCADE
    )
    issued_date_time = models.DateTimeField('Время выдачи', auto_now_add=True)


class UserCourseSettings(BaseModel):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='user_course_settings',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        verbose_name='Курсы',
        related_name='course_user_settings',
        on_delete=models.CASCADE,
    )
    start_course = models.DateTimeField('Время начала')
    end_course = models.DateTimeField('Время окончания', null=True, blank=True)

    class Meta:
        verbose_name = 'User Course Settings'
        verbose_name_plural = 'User Course Settings'
        ordering = ['-created']
        db_table = 'user_course_setting'

    def __str__(self):
        return f'{self.user}, курс: {self.course}'
