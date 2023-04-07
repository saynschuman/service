from django.db.models.signals import post_save
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from backend.extra.tasks import new_message
from backend.users.models import User
from backend.mess.models import Chat, UserMessage


@receiver(post_save, sender=Chat)
def add_users_to_chat(sender, instance, **kwargs):
    if instance.is_support:
        admins = User.objects.filter(user_status=User.STATUS_ADMIN)
        instance.users.add(*admins)
    elif instance.is_teacher:
        try:
            teacher = instance.course.author
        except AttributeError:
            pass
        else:
            instance.users.add(teacher)
    elif instance.is_group:
        # TODO: добавить по дате начала обучения ???
        groups = User.objects.filter(
            user_status=User.STATUS_CLIENT,
            courses__in=(instance.course,),
            company=instance.company,
        )
        instance.users.add(*groups)


@receiver(post_save, sender=UserMessage)
def send_email_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("notifications", {
            "type": "new_chat_message",
            "message": f'Новое сообщение от {instance.author}',
            "message_for": instance.user.pk,
            "chat_id": instance.message.chat.pk,
            "author_id": instance.author_id,
            "author": instance.author,
            "chat_status": instance.chat_status,
            "message_text": instance.message_text,
            "message_id": instance.id
        })

    if created and instance.user.is_admin and not instance.is_read:
        new_message.delay(instance.message_id)
