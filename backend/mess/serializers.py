from rest_framework import serializers

from backend.users.models import User
from .models import Chat, Message, UserMessage


class ReadChatMessagesSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()

    def update_is_read(self, validated_data, user):
        try:
            chat = Chat.objects.get(
                id=validated_data["chat_id"],
                users=user.id,
            )
        except Chat.DoesNotExist as ex:
            return False, f'Chat ID:{validated_data["chat_id"]} for user ID:{user.id} not found'
        else:
            UserMessage.objects.filter(
                user=user,
                message__chat=chat,
                is_read=False,
            ).update(is_read=True)

        return True, f'All chat ID:{validated_data["chat_id"]} messages for the user ID:{user.id} are read'


class _UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'user_status',
            'time_limitation',
            'company',
        )


class ChatSerializer(serializers.ModelSerializer):
    list_users = _UserSerializer(read_only=True, many=True, source='users')
    last_message_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Chat
        fields = (
            'id',
            'chat_status',
            'users',
            'course',
            'company',
            'num_messages',
            'list_users',
            'last_message_date',
        )


class MessageSerializer(serializers.ModelSerializer):
    user = _UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class MassMessageSerializer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.IntegerField(min_value=1)
    )
    message = serializers.CharField()

    def create(self, validated_data, user):
        result = []
        chat_status = user.user_status

        clients = validated_data['users']
        for client in clients:
            chat = Chat.objects.filter(
                chat_status=chat_status,
                users=client,
            ).first()
            if not chat:
                chat = Chat.objects.create(
                    chat_status=chat_status,
                )
                chat.users.add(client)
                chat.save()

            message = Message.objects.create(
                mess=validated_data['message'],
                chat=chat,
                user=user,
            )
            result.append({'chat_id': chat.id, 'message_id': message.id, 'user_id': client})
        return result


class FirebaseSettingsSerializer(serializers.Serializer):
    apikey = serializers.CharField(required=True)
