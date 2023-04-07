import json
import os

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.conf import settings

from backend.api_v1.permissions import IsModerator, is_administrator, is_moderator
from backend.api_v1.utils import response_success, response_error
from backend.constants import INVALID_DATA
from backend.courses.models import (
    Material,
    Course,
    Task,
    Tag,
    Question,
    Answer,
    MaterialPassing,
    Passing,
)
from backend.courses.serializers.atbm_serializers import MaterialPassingSerializer, AnswerSerializer, TagSerializer
from backend.courses.serializers.course_serializers import CourseAdminSerializer, CourseModeratorSerializer, \
    ItemCourseAdminSerializer, ItemCourseModeratorSerializer
from backend.courses.serializers.material_serializers import MaterialSerializer, MaterialCopySerializer
from backend.courses.serializers.passing_serializers import TestPassingSerializer, OutOfTimeTestPassingSerializer
from backend.courses.serializers.question_serializers import QuestionSerializer, QuestionFileSerializer
from backend.courses.serializers.task_serializers import ModeratorTaskSerializer, TaskCopySerializer, CommonTaskSerializer


class CourseListCreate(generics.ListCreateAPIView):
    """
    Курсы
    """
    serializer_class = CourseAdminSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    filterset_fields = (
        'title',
        'author',
        'tag',
        'created',
        'id',
    )

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated and is_administrator(self.request.user):
            return Course.objects.with_select_related().with_prefetch_related().with_annotations()
        elif self.request.user and self.request.user.is_authenticated and is_moderator(self.request.user):
            return Course.objects.filter(
                Q(moderators=self.request.user) | Q(author=self.request.user)
            ).with_prefetch_related().with_annotations()

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated and is_administrator(self.request.user):
            return CourseAdminSerializer
        elif self.request.user and self.request.user.is_authenticated and is_moderator(self.request.user):
            return CourseModeratorSerializer

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated and is_moderator(self.request.user):
            serializer.validated_data['author'] = self.request.user
        super().perform_create(serializer)


class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Курсы
    """
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated and is_administrator(self.request.user):
            return Course.objects.with_select_related().with_prefetch_related().with_annotations()
        elif self.request.user and self.request.user.is_authenticated and is_moderator(self.request.user):
            return Course.objects.filter(
                Q(moderators=self.request.user) | Q(author=self.request.user)
            ).with_prefetch_related().with_annotations()

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated and is_administrator(self.request.user):
            return ItemCourseAdminSerializer
        elif self.request.user and self.request.user.is_authenticated and is_moderator(self.request.user):
            return ItemCourseModeratorSerializer


class MaterialListCreate(generics.ListCreateAPIView):
    """
    Материалы
    """

    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = '__all__'
    lookup_field = 'id'
    filterset_fields = (
        'course',
        'title',
        'is_download',
        'created',
        'id',
        'parent',
    )
    search_fields = ['title']


class MaterialDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Материалы
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        old_pdf_name = instance.pdf
        old_video_name = instance.video

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        response = Response(serializer.data)

        if request.data.get('video'):
            try:
                os.remove(f'{settings.MEDIA_ROOT}/{old_video_name}')
                os.rename(f'{settings.MEDIA_ROOT}/{instance.video}', f'{settings.MEDIA_ROOT}/{old_video_name}')
                instance.video = old_video_name
                instance.save()
            except NotADirectoryError:
                pass

        if request.data.get('pdf'):
            try:
                os.remove(f'{settings.MEDIA_ROOT}/{old_pdf_name}')
                os.rename(f'{settings.MEDIA_ROOT}/{instance.pdf}', f'{settings.MEDIA_ROOT}/{old_pdf_name}')
                instance.pdf = old_pdf_name
                instance.save()
            except NotADirectoryError:
                pass

        return response

    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'


class MaterialCopy(generics.GenericAPIView):
    """
    Копирование материала
    """
    serializer_class = MaterialCopySerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            material = serializer.create(serializer.data)
            serialized_obj = MaterialSerializer(material)
            return Response(serialized_obj.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MaterialFullCopy(generics.GenericAPIView):
    """
    Полное копирование материала
    """
    serializer_class = MaterialCopySerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            material = serializer.create_full(serializer.data)
            serialized_obj = MaterialSerializer(material)
            return Response(serialized_obj.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MaterialSingleCopy(generics.GenericAPIView):
    """
    Одиночное копирование материала
    """
    serializer_class = MaterialCopySerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            material = serializer.single_create(serializer.data)
            serialized_obj = MaterialSerializer(material)
            return Response(serialized_obj.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskCopy(generics.GenericAPIView):
    """
    Копирование задания
    """
    serializer_class = TaskCopySerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            task = serializer.copy(serializer.data)
            serialized_obj = CommonTaskSerializer(task)
            return Response(serialized_obj.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListCreate(generics.ListCreateAPIView):
    """
    Задания
    """

    queryset = Task.objects.with_prefetch_related()
    serializer_class = ModeratorTaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    filterset_fields = (
        'id',
        'title',
        'created',
        'is_necessarily',
        'is_final',
        'is_hidden',
        'material',
        'material__course',
        'is_active',
    )


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Задания
    """

    queryset = Task.objects.all()
    serializer_class = ModeratorTaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'


class QuestionListCreate(generics.ListCreateAPIView):
    """
    Вопросы
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    filterset_fields = (
        'id',
        'is_free_answer',
        'tasks',
        'score',
    )


class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Вопросы
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'


class QuestionFromFileCreation(generics.GenericAPIView):
    """
    Добавление вопросов из файла
    """

    serializer_class = QuestionFileSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    http_method_names = ('post',)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        question_file = request.FILES.get('file')
        if serializer.is_valid():
            created, message, result_list, code = serializer.create_questions(serializer.data, question_file)
            if created:
                res = json.dumps(['id: {}, text: {}'.format(question.id, question.text) for question in result_list])
                return response_success(code, message, res, status.HTTP_201_CREATED)
            else:
                return response_error(code, message, serializer.errors, status.HTTP_400_BAD_REQUEST)
        return response_error(INVALID_DATA, 'invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)


class TestPassingViewSet(ModelViewSet):
    """
    Прохождение тестов клиентами
    """
    serializer_class = TestPassingSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'task',
        'task__material__course',
        'user',
        'success_passed',
        'is_trial',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return Passing.objects.with_select_related()


class TestPassingDetail(generics.RetrieveUpdateAPIView):
    """
    Прохождение тестов клиентом
    """

    queryset = Passing.objects.all()
    serializer_class = OutOfTimeTestPassingSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'


class MaterialPassingViewSet(ModelViewSet):
    """
    Прохождение материалов клиентами
    """

    queryset = MaterialPassing.objects.all()
    serializer_class = MaterialPassingSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'user',
        'material',
        'material__course',
        'status',
    )
    ordering_fields = '__all__'


class AnswerListCreate(generics.ListCreateAPIView):
    """
    Ответы
    """

    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    filterset_fields = (
        'id',
        'question',
        'is_true',
        'rank',
    )


class AnswerDetail(generics.RetrieveUpdateAPIView):
    """
    Ответы
    """

    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'


class TagListCreate(generics.ListCreateAPIView):
    """
    Тэги
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    filterset_fields = (
        'tag',
        'created',
        'id',
    )


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Тэги
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'
