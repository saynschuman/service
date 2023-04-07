from __future__ import absolute_import, unicode_literals

from backend.extra.utils import get_email_data, make_log
from celery import shared_task
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.db.models import Q

from backend.mess.models import Message
from backend.users.models import Company
from backend.courses.models import Tag


@shared_task
def new_message(mess_id):
    """
    Новое сообщение
    """

    mes = Message.objects.get(id=mess_id)
    current_site = Site.objects.get_current()
    context = {
        'message': mes,
        'domain': current_site.domain,
    }

    subject = f'Новое сообщение в чате с сайта lk.promrg.ru от {mes.user.username}'
    message = get_template('extra/new_message.html').render(context)

    try:
        connection, from_email = get_email_data()
        email = EmailMessage(
            subject,
            message,
            from_email,
            [from_email],
            connection=connection,
        )
        email.content_subtype = 'html'
        email.send()
    except Exception as ex:
        message = f'Ошибка отправки письма для сообщения ID:{mes.id}\n{ex}'
        make_log(message)


@shared_task
def clean_tags():
    """
    Чистим непривязаные теги.
    """
    deleted = Tag.objects.filter(courses__isnull=True).delete()
    print(f"Deleted unused {deleted[0]} tags.")


@shared_task
def clean_companies():
    """
    Чистим неиспользуемые компании.
    """
    deleted = Company.objects.filter(Q(company_users__isnull=True) & Q(company_chats__isnull=True)).delete()
    print(f"Deleted unused {deleted[0]} companies.")
