from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.courses.models import Passing
from backend.courses.models import Task
from backend.courses.tasks import close_attempt
from django.conf import settings

@receiver(post_save, sender=Passing)
def fill_max_points(sender, instance, created, **kwargs):
    """
    Сохранение максимально возможного кол-ва баллов за тестирование
    """
    if created:
        max_points = instance.task.get_questions_score()
        instance.max_points = max_points
        instance.save(update_fields=['max_points'])

@receiver(post_save, sender=Passing)
def auto_close_attempt(sender, instance, created, **kwargs):
    """
    создание задачи для автоматического закрытия попытки, если время истекло
    """
    if created:
        task = Task.objects.get(id=instance.task.pk)
        timeout = task.travel_time.second + task.travel_time.minute * \
                60 + task.travel_time.hour * 60 * 60

        if not settings.DJANGO_DEVELOPMENT:
            close_attempt.apply_async((instance.pk,), countdown=timeout)
