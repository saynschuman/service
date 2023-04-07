from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Sum
from django.http import Http404
from django.views.generic import TemplateView, DetailView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backend.api_v1.permissions import IsAdministrator, IsModerator
from .models import Chat, Message, FirebaseSettings
from .serializers import (
    ChatSerializer,
    MessageSerializer,
    MassMessageSerializer,
    FirebaseSettingsSerializer,
    ReadChatMessagesSerializer,
)


class ChatViewSet(generics.ListCreateAPIView):
    """
    Чаты
    """
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ('id', 'chat_status', 'users', 'course', 'company', 'created')
    ordering_fields = '__all__'

    def get_queryset(self):
        return Chat.objects.with_prefetch_related().with_annotations()


class ChatDeleteView(generics.DestroyAPIView):
    """
    Удаление чатов
    """
    queryset = Chat.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsModerator)


class MessageViewSet(generics.ListCreateAPIView):
    """
    Сообщения чатов
    """
    queryset = Message.objects.select_related('user')
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ('id', 'chat', 'user', 'created')
    ordering_fields = '__all__'


class EmptyChatView(LoginRequiredMixin, TemplateView):
    template_name = 'mess/chats.html'


class SupportChatView(LoginRequiredMixin, TemplateView):
    template_name = 'mess/support_chat.html'


class TeacherChatView(LoginRequiredMixin, TemplateView):
    template_name = 'mess/teacher_chat.html'


class GroupChatView(LoginRequiredMixin, TemplateView):
    template_name = 'mess/group_chat.html'


class TeacherNavView(LoginRequiredMixin, TemplateView):
    template_name = 'mess/support_nav.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_admin:
            chats = Chat.objects.filter(chat_status=Chat.STATUS_TEACHER)
        elif self.request.user.is_moderator:
            chats = Chat.objects.filter(chat_status=Chat.STATUS_TEACHER, users__in=(self.request.user,))
        else:
            chats = None

        context.update({
            'chats': chats,
        })
        return context


class SupportNavView(LoginRequiredMixin, TemplateView):
    template_name = 'mess/support_nav.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'chats': Chat.objects.filter(chat_status=Chat.STATUS_SUPPORT, users__in=(self.request.user,)),
        })
        return context


class ItemChatView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = 'mess/item_chat.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.is_admin or self.request.user.user_chats.filter(pk=self.kwargs['pk']).exists():
            return obj
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        chat_types = {
            0: 's_chat',
            1: 't_chat',
            2: 'g_chat'
        }
        context.update({
            'chat_type': chat_types[obj.chat_status],
        })
        return context


class UserMessageView(ModelViewSet):
    """
    Прочтение сообщений пользователем
    """
    serializer_class = ReadChatMessagesSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            is_ok, message = serializer.update_is_read(serializer.data, request.user)
            if is_ok:
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUnreadMessageCountView(APIView):
    """
    Получение кол-ва непрочитанных сообщений для пользователя
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        {
            chats: [
                {chat_id: XX, unread_messages: XX},
                {chat_id: XX, unread_messages: XX},
                ...
            ],
            total_unread_messages: XX
        }
        """
        chats = Chat.objects.filter(
            messages__user_messages__user=request.user,
            messages__user_messages__is_read=False,
        ).annotate(
            chat_id=F('id'),
            chat_type=F('chat_status'),
            unread_messages=Count('messages__user_messages'),
        ).order_by('id').values('chat_id', 'chat_type', 'unread_messages')
        res = chats.aggregate(total_unread_messages=Sum('unread_messages'))
        res.update({
            'chats': list(chats)
        })
        return Response(res, status=status.HTTP_200_OK)


class MassMessageView(generics.GenericAPIView):
    """
    Массовая рассылка сообщений
    """
    serializer_class = MassMessageSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdministrator)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            messages = serializer.create(serializer.data, request.user)
            return Response(messages, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetFirebaseSettingsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        snippets = FirebaseSettings.objects.first()
        serializer = FirebaseSettingsSerializer(snippets)
        return Response(serializer.data)


class ChangeFirebaseSettingsViewSet(ModelViewSet):
    serializer_class = FirebaseSettingsSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdministrator)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            obj = FirebaseSettings.objects.first()
            if not obj:
                obj = FirebaseSettings.objects.create(
                    apikey=serializer.data.get('apikey'),
                )
            else:
                obj.apikey = serializer.data.get('apikey')
                obj.save()
            return Response(obj.apikey, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
