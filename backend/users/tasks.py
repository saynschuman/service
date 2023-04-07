from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from backend.users.models import User, UserOnlineHistory


@shared_task
def check_clients():
    """
    Проверка клиента на временные ограничения
    end_course + 90 дней
    """
    users = User.objects.filter(
        user_status=User.STATUS_CLIENT,
        is_active=True,
        end_course__isnull=False,
    )

    updated = 0
    for user in users:
        end_course = user.end_course + timedelta(days=90)
        if now().date() >= end_course:
            user.is_active = False
            user.save()
            updated += 1
    print('find {} clients'.format(users.count()))
    print('updated {} clients'.format(updated))


@shared_task
def online_clients_history():
    """
    Проверяем количество активных клиентов и обновляем данные в истории
    """
    r_date = now().replace(hour=0, minute=0, second=0, microsecond=0)
    clients_count = User.get_online_clients_day_count(r_date)
    UserOnlineHistory.objects.update_or_create(date=r_date, defaults={'active_clients_count': clients_count})
    print(f"{clients_count} was active on {now()}")
