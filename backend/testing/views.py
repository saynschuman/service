from datetime import datetime

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from backend.api_v1.permissions import IsClient, IsModerator, ClientTime
from .models import UserAnswer
from .serializers import UserAnswerSerializer, ModeratorUserAnswerSerializer


@api_view()
def server_time(request):
    return Response({'server_time': datetime.now()})


class ModeratorUserAnswerViewSet(ModelViewSet):
    """
    Получение ответов для модератора
    """
    queryset = UserAnswer.objects.all()
    serializer_class = ModeratorUserAnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'passing',
        'question',
        'answer',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        if self.request.user.is_admin:
            qs = UserAnswer.objects.all()
        else:
            qs = UserAnswer.objects.filter(
                Q(passing__task__material__course__author=self.request.user.pk) |
                Q(passing__task__material__course__moderators=self.request.user.pk)
            )
        return qs


class ModeratorUserAnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Проверка ответов модератором
    """
    queryset = UserAnswer.objects.all()
    serializer_class = ModeratorUserAnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_admin:
            qs = UserAnswer.objects.all()
        else:
            qs = UserAnswer.objects.filter(
                Q(passing__task__material__course__author=self.request.user.pk) |
                Q(passing__task__material__course__moderators=self.request.user.pk)
            )
        return qs


class UserAnswerClientListCreate(generics.ListCreateAPIView):
    """
    Ответы клиента на тест
    """
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = (
        'id',
        'passing',
        'question',
        'answer',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return UserAnswer.objects.filter(passing__user=self.request.user)


class UserAnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Ответы клиента на тест
    """
    # parser_classes = (FormParser, MultiPartParser)
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    lookup_field = 'id'

    def get_queryset(self):
        return UserAnswer.objects.filter(passing__user=self.request.user)
