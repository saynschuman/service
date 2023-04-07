from celery import shared_task
from celery.utils.log import get_task_logger
from backend.courses.models import Passing

logger = get_task_logger(__name__)

@shared_task
def close_attempt(pk):
    """
    Закрытие начатой попытки прохождения теста
    """

    passing = Passing.objects.get(pk=pk)

    logger.info(f'finish_time {passing.finish_time}')

    if not passing.finish_time:
        logger.info(f"Автоматическое закрытие попытки {pk} по истечении времени")
        passing.check_passing()
