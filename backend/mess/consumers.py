from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from backend.users.models import User
from backend.mess.exceptions import ClientError
from backend.mess.models import Chat, Message, UserMessage


class SupportChatConsumer(JsonWebsocketConsumer):
    chat_name = 'support_chat_'
    chat_status = Chat.STATUS_SUPPORT
    chat = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

        user_data = self.scope['url_route']['kwargs']
        user_id = user_data.get('user_id')
        user_token = user_data.get('token')

        # TODO: проверить token пользователя
        if user_id and user_token:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
            else:
                self.user = user

    def connect(self):
        """
        Соединение, добавление канала в группу
        """

        # TODO: проверить token пользователя
        if self.user:
            self.chat = self.get_chat(self.user)
            self.chat_name += str(self.chat.pk)
            async_to_sync(self.channel_layer.group_add)(self.chat_name, self.channel_name)
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        """
        При разрыве соединения очищаем группу
        """
        async_to_sync(self.channel_layer.group_discard)(self.chat_name, self.channel_name)

    def receive_json(self, content):
        """
        Обмен сообщениями в группе
        """
        command = content.get('command', None)

        try:
            if command == 'send':
                message = self.save_message(self.user, self.chat, content['message'])
                async_to_sync(self.channel_layer.group_send)(
                    self.chat_name,
                    {
                        'type': 'send.message',
                        'chat_user': self.scope['user'].username,
                        'message': message.mess,
                        'message_id': message.id,
                        'user_id': self.user.id,
                    }
                )
        except ClientError as e:
            self.send_json({'error': e.code})

    def send_message(self, event):
        """
        Отправка сообщения в чат
        """
        # print(event)
        self.send_json({
            'message': event['message'],
            'user_id': event['user_id'],
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        })

    def get_chat(self, user):
        """
        Получаем или создаем чат
        """
        if user.is_admin or user.is_moderator:
            chat_id = self.scope['url_route']['kwargs']['chat_id']
            try:

                # Если пользователь является преподавателем, то он может получить
                # только свои чаты, администратор же может получить все чаты
                payload = {}
                if user.is_moderator:
                    payload = {
                        'users__in': (user,)
                    }

                chat = Chat.objects.get(
                    pk=chat_id,
                    chat_status=self.chat_status,
                    **payload,
                )
            except Chat.DoesNotExist:
                # TODO: действия по инициализации чата от лица тех.поддержки или препода
                print('нужно создать чат от лица админа или модератор')

        else:
            chat = Chat.objects.filter(
                chat_status=self.chat_status,
                users__in=(user,),
            ).first()
            if not chat:
                payload = {
                    'chat_status': self.chat_status,
                    'course': user.courses.first() or None,
                    'company': user.company or None,
                }
                chat = Chat(**payload)
                chat.save()
                chat.users.add(user)
        return chat

    @staticmethod
    def save_message(user, chat, message):
        message = Message.objects.create(
            user=user,
            chat=chat,
            mess=message,
        )
        for chat_user in chat.users.all():

            # Если пользователь является создателем сообщения, то автоматом сообщение для него прочтено
            if chat_user.id == user.id:
                is_read = True
            else:
                is_read = False

            UserMessage.objects.create(
                message_id=message.id,
                user_id=chat_user.id,
                is_read=is_read,
                author=user.username,
                author_id=user.id,
                chat_status=chat.chat_status,
                message_text=message.mess
            )
        return message


class TeacherChatConsumer(SupportChatConsumer):
    chat_name = 'teacher_chat_'
    chat_status = Chat.STATUS_TEACHER


class GroupChatConsumer(SupportChatConsumer):
    chat_name = 'group_chat_'
    chat_status = Chat.STATUS_GROUP
