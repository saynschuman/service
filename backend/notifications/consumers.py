import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

class NotificationConsumer(JsonWebsocketConsumer):
    room_group_name = 'notifications'
    user_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None
        user_data = self.scope['url_route']['kwargs']
        self.user_id = user_data.get('user_id')

        # TODO: сделать проверку по токену

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )


        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = hasattr(text_data_json, 'message') and text_data_json.message
        message_for = hasattr(text_data_json, 'message_for') and text_data_json.message_for
        chat_id = hasattr(text_data_json, 'chat_id') and text_data_json.chat_id
        author_id = hasattr(text_data_json, 'author_id') and text_data_json.author_id
        chat_status = hasattr(text_data_json, 'chat_status') and text_data_json.chat_status
        message_text = hasattr(text_data_json, 'message_text') and text_data_json.message_text
        author = hasattr(text_data_json, 'author') and text_data_json.author
        message_id = hasattr(text_data_json, 'message_id') and text_data_json.message_id

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'new_chat_message',
                'message': message,
                'message_id': message_id,
                'message_for': message_for,
                'chat_id': chat_id,
                'author_id': author_id,
                'chat_status': chat_status,
                'message_text': message_text,
                'author': author
            }
        )

    # Receive message from room group
    def new_chat_message(self, event):
        message = event['message']
        message_for = event['message_for']
        chat_id = event['chat_id']
        author_id = event['author_id']
        chat_status = event['chat_status']
        message_text = event['message_text']
        author = event['author']
        message_id = event['message_id']

        # Send message to WebSocket
        if message_for == self.user_id and self.user_id != author_id:
            self.send(text_data=json.dumps({
            'message': message,
            'message_id': message_id,
            'message_for': message_for,
            'chat_id': chat_id,
            'author_id': author_id,
            'chat_status': chat_status,
            'message_text': message_text,
            'author': author,
        }))
