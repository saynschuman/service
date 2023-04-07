from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.testing.models import UserAnswer


@receiver(post_save, sender=UserAnswer)
def end_test_passing(sender, instance, **kwargs):
    # если ответ дается для пробного прохождения тестирования, то ничего не делать!
    if instance.passing.is_trial:
        return False

    # пересчет тестирования после оценки ответа преподавателем (время окончания тестирования не должно менятся)
    if instance.question.is_free_answer and instance.user_points is not None:
        instance.passing.check_passing(finish=False)
        return False

    # пересчет тестирования, если все ответы в тесте пройдены вовремя
    num_questions = instance.passing.task.num_questions
    num_answers = instance.passing.user_answers.all().count()
    if num_questions == num_answers and not instance.passing.finish_time:
        instance.passing.check_passing(finish=True)
        return False
