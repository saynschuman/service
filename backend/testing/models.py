from django.core.validators import MinValueValidator
from django.db import models

from backend.courses.models import Question, Answer, Course, Task, Passing
from backend.helpers import BaseModel
from backend.users.models import User


class UserAnswer(BaseModel):
    """
    Ответ пользователя на вопрос из теста
    """
    passing = models.ForeignKey(
        Passing,
        verbose_name='Прохождение теста',
        related_name='user_answers',
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        related_name='user_answers',
        on_delete=models.CASCADE,
    )
    answer = models.ForeignKey(
        Answer,
        verbose_name='Выбранный ответ',
        related_name='user_answers',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    answers = models.ManyToManyField(Answer, verbose_name='Выбранные ответы', related_name='u_answers', blank=True)
    text = models.TextField('Ответ в произвольной форме', null=True, blank=True)
    file = models.FileField('Файл пользователя', upload_to='user_answer/', null=True, blank=True)
    user_points = models.SmallIntegerField('Баллы за ответ', validators=[MinValueValidator(0)], null=True, blank=True)
    verifier = models.ForeignKey(
        User,
        verbose_name='Проверяющий',
        related_name='user_answers',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-created']
        unique_together = ['passing', 'question']

    def __str__(self):
        return str(self.id)

    def get_user_points(self):
        """
        Получение баллов за ответ
            - если ответ в свободной форме, то получать self.user_points
            - если ответ не в сободной форме, то сравнивать выбранные ответы
            со списком правильных ответов, баллы начисляются только при полном совпадении списков
        :return: int, баллы за ответ
        """
        user_points = 0
        if self.question.is_free_answer:
            user_points = self.user_points or 0
        else:
            if self.answer:
                self.answers.add(self.answer)
            correct_answers = list(self.question.correct_answer)
            user_answers = list(self.answers.values_list('id', flat=True))
            if correct_answers == user_answers:
                user_points = self.question.score

        return user_points

    @property
    def max_points(self):
        return self.question.score

    @property
    def variants(self):
        return self.question.variants

    @property
    def correct_answer(self):
        return self.question.correct_answer


class Attempts(BaseModel):
    """
    Попытки прохождения теста пользователем ???
    """
    course = models.ForeignKey(Course, verbose_name='Курс', related_name='attempts', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='attempts', on_delete=models.CASCADE)
    num_attempts = models.SmallIntegerField('Кол-во попыток', default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Кол-во попыток'
        verbose_name_plural = 'Кол-во попыток'

    def __str__(self):
        return self.user.username + ' - ' + self.course.title
