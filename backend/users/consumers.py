import time
from datetime import date, datetime

from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from .models import User, UserDayActivity, UserActivity


class UserActivityConsumer(JsonWebsocketConsumer):
    room_group_name = 'online_users'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_activity = None
        self.start_time = 0

    def chat_message(self, event):
        pass

    def connect(self):
        # TODO: сделать проверку по токену
        # TODO: возможно получить пользователя по токену
        self.start_time = time.time()
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': 'message'
            }
        )

        # if auth_token:
        #     obj = AccessToken(auth_token)
        #     try:
        #         obj.verify()
        #     except TokenError:
        #         self.close()
        #     else:
        #         self.accept()

    def receive_json(self, content, **kwargs):
        if 'user' in content:
            try:
                user = User.objects.get(pk=content['user'])
                user.last_active = datetime.now()
                user.save()

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': 'message'
                    }
                )
            except User.DoesNotExist:
                pass
            else:
                payload = {
                    'user': user,
                    'day': date.today(),
                    'course_id': content.get('course'),
                }
                # self.user_activity, _ = UserDayActivity.objects.get_or_create(**payload)
                UserActivity.objects.create(user=user, headers=str(content), payload=str(content),
                                            course_id=content.get('course'))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': 'message'
            }
        )

        if self.user_activity:
            session_time = time.time() - self.start_time
            total_time = self.user_activity.seconds + session_time
            self.user_activity.seconds = total_time
            self.user_activity.save()

            async_to_sync(self.channel_layer.group_discard)(
                'online_users',
                self.channel_name
            )


class OnlineUsersConsumer(JsonWebsocketConsumer):
    room_group_name = 'online_users'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send_json(dict(online_users='connect'))

    def receive_json(self, content, **kwargs):
        ONLINE_DELTA_MIN = 15
        delta = content.get('timedelta_mins')
        # token = content.get('token')

        # from rest_framework_simplejwt.backends import TokenBackend
        # valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)

        if delta is None:
            delta = ONLINE_DELTA_MIN
        else:
            try:
                delta = int(delta)
            except ValueError:
                delta = ONLINE_DELTA_MIN
        count = User.get_online_clients_count(delta)
        self.send_json({'online_users': count})

    def chat_message(self, event):
        count = User.get_online_clients_count(15)
        self.send_json({'online_users': count})



