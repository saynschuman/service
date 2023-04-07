import datetime
from collections import Counter

from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import APIException

from backend.api_v1.permissions import IsClient, ClientTime, IsCurator, IsModerator
from backend.api_v1.utils import response_error
from backend.constants import INVALID_TIME_INTERVAL, INVALID_DATA, EXCEEDED_NUMBER
from backend.courses.models import (
    Course,
    Tag,
    Material,
    Task,
    Question,
    Answer,
    MaterialPassing,
    Passing,
    Bookmark,
    UserCourseSettings
)
from backend.courses.serializers.atbm_serializers import (
    BookmarkSerializer,
    TagSerializer,
    MaterialPassingSerializer,
    AnswerSerializer,
)
from backend.courses.serializers.course_serializers import (CourseClientSerializer, UserCourseSettingsSerializer,
                                                            UserCourseSettingsDetailSerializer)
from backend.courses.serializers.material_serializers import MaterialClientSerializer
from backend.courses.serializers.passing_serializers import ClientTestPassingSerializer, TestPassingSerializer
from backend.courses.serializers.question_serializers import QuestionSerializer
from backend.courses.serializers.task_serializers import CommonTaskSerializer
from backend.users.models import User
from rest_framework import serializers


class DuplicateRecording(APIException):
    status_code = 400
    default_detail = "Похожая запись уже существует."
    default_code = "duplicate_recording"


class CourseClientViewSet(ModelViewSet):
    """
    Курсы клиента
    """

    serializer_class = CourseClientSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'title',
        'author',
        'tag',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return Course.objects.with_select_related().filter(
            users__in=[self.request.user],
            is_active=True,
        )

class _UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'user_status',
        )

class CourseClientAllViewSet(ModelViewSet):
    """
    Все пользователи с таким же курсом как у текущего
    """

    serializer_class = _UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        # Получаем курсы текущего пользователя
        user_courses = Course.objects.with_select_related().filter(
            users__in=[self.request.user],
            is_active=True,
        )

        # Получаем список пользователей, которые имеют хотя бы один из курсов текущего пользователя
        users = User.objects.filter(
            courses__in=user_courses
        ).distinct()

        return users

class MaterialClientViewSet(ModelViewSet):
    """
    Материалы курсов клиента
    """

    queryset = Material.objects.all()
    serializer_class = MaterialClientSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'course',
        'title',
        'is_download',
        'parent',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return Material.objects.filter(
            course__users__in=[self.request.user],
            course__is_active=True,
            is_active=True,
        )


def get_old_or_new_task_for_user(user, material):
    task = None

    current_material_tasks = Task.objects.filter(material=material, is_active=True)

    # TODO:
    # Проверить есть ли прохождения этого теста другими пользователем
    # Если нету - проходить этот тест
    # Если есть - брать следующий вариант

    all_passings = Passing.objects.filter(user=user, success_passed__in=[2, 3, 4], task__material=material)
    all_passings_count = all_passings.count()
    last_passing = all_passings.first()
    passing_tasks = []
    for p in all_passings:
        passing_tasks.append(p.task)

    if all_passings_count < 3:
        task = current_material_tasks.first()
        # print('passings less then 3')
    else:
        three_attempts_passed = all_passings[0].task == all_passings[1].task == all_passings[2].task
        if three_attempts_passed:
            all_tasks = Task.objects.filter(material=material, is_active=True)
            passing_collection = dict(Counter(passing_tasks))
            passed_tasks = passing_collection.values()
            if all_passings_count < all_tasks.count() * 3:
                for t in all_tasks:
                    if t not in passing_tasks:
                        task = t
                # print('passings more then 3 but passed not all variants')
            else:
                min_passing = min(passed_tasks)
                task_of_min_passings = None
                for task, num_passings in passing_collection.items():
                    if num_passings == min_passing:
                        task_of_min_passings = task
                task = task_of_min_passings
                # print('passed all variants and chose task with min passings')
        else:
            # print('repeat last passing')
            task = last_passing.task

    return task



def get_user_passes_task(user) -> Task:
    passing = Passing.objects.filter(success_passed=5, user=user).first()
    if passing:
        return passing.task


class TaskFilter(FilterSet):
    class Meta:
        model = Task
        fields = {'material__course': ['in'], 'id': ['exact'], 'material': ['in'], 'title': ['contains'],
                  'is_necessarily': ['exact'], 'is_final': ['exact']}


class TaskClientViewSet(ModelViewSet):
    """
    Задания материалов курсов клиента
    """

    queryset = Task.objects.all()
    serializer_class = CommonTaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = TaskFilter
    filterset_fields = (
        'id',
        'material',
        'material__course',
        'title',
        'is_necessarily',
        'is_final',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        from functools import reduce
        materials = {}

        all_user_materials = reduce(lambda x, y: x + y,
                                    [[material for material in course.materials.filter(is_active=True)] for course in
                                     self.request.user.courses.filter(is_active=True)])

        for material in all_user_materials:
            task = get_old_or_new_task_for_user(self.request.user, material)

            if task:
                materials.update({material.pk: task})
                continue

        return Task.objects.filter(
            material__course__users__in=[self.request.user],
            material__course__is_active=True,
            material__is_active=True,
            pk__in=[materials.get(mk).id for mk in materials.keys()]
        ).order_by('rank')


class QuestionClientViewSet(ModelViewSet):
    """
    Вопросы заданий материалов курсов клиента
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'tasks',
        'is_free_answer',
        'score',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return Question.objects.filter(
            tasks__material__course__users__in=[self.request.user],
            tasks__material__course__is_active=True,
            tasks__material__is_active=True,
        )


class TestPassingClientListCreate(generics.ListCreateAPIView):
    """
    Прохождение тестов клиентом
    """

    queryset = Passing.objects.all()
    serializer_class = ClientTestPassingSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'task',
        'success_passed',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return Passing.objects.filter(user=self.request.user).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Еще есть интервал пересдачи - проверить его, исключая тестовые (is_trial=True)
        # Если у предыдущей пересдачи по такому же заданию стоит out_of_time, то интервал не проверять
        data = serializer.validated_data

        if data['is_trial']:
            # если прохождение тестовое (is_trial=True),
            # проверить для таска кол-во уже созданных тестовых прохождений (trial_attempts)
            try:
                task = Task.objects.get(id=data['task'].id)
            except Task.DoesNotExist:
                message = f"Task id: {data['task']} does not exist"
                return response_error(INVALID_DATA, message, serializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                trial_attempts = task.trial_attempts
                trial_passings = Passing.objects.filter(is_trial=True, user=self.request.user, task=task)
                if trial_passings.count() >= trial_attempts:
                    message = f"Exceeded the number of trial attempts in the task id: {data['task']}"
                    return response_error(EXCEEDED_NUMBER, message, serializer.data, status=status.HTTP_400_BAD_REQUEST)
        else:
            previous_passing = Passing.objects.filter(
                task=data['task'],
                user=self.request.user,
                is_trial=False,
            ).order_by('-created').first()
            if previous_passing:
                if not previous_passing.finish_time:
                    message = f"Previous passing (id: {previous_passing.id}) has no finish_time"
                    return response_error(INVALID_TIME_INTERVAL, message, serializer.data,
                                          status=status.HTTP_400_BAD_REQUEST)
                past_time = now() - previous_passing.finish_time
                retake_seconds = previous_passing.task.retake_seconds
                retake_timedelta = datetime.timedelta(seconds=retake_seconds)
                if not previous_passing.out_of_time:
                    if past_time < retake_timedelta:
                        seconds = retake_timedelta - past_time
                        message = f"Try passing the test through {seconds.total_seconds()}"
                        return response_error(INVALID_TIME_INTERVAL, message, serializer.data,
                                              status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class EndTestPassingClientView(APIView):
    """
    Окончание прохождения теста клиентом
    """

    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)

    def get(self, request, pk, format=None):
        try:
            passing = Passing.objects.get(pk=pk)

        except Passing.DoesNotExist:
            return Response('Object does not exist', status=status.HTTP_400_BAD_REQUEST)

        else:
            is_passed = passing.check_passing()
            serializer = TestPassingSerializer(passing)

            if passing.user != self.request.user:
                return Response('User not correct', status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data)


class BookmarkListCreate(generics.ListCreateAPIView):
    """
    Закладки клиена для материалов
    """

    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'material',
        'title',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class BookmarkDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Закладки клиена для материалов
    """

    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    lookup_field = 'id'

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class TagClientViewSet(ModelViewSet):
    """
    Тэги курсов клиента
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'tag',
        'created',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return Tag.objects.filter(
            courses__users__in=[self.request.user],
            courses__is_active=True,
        )


class MaterialPassingListCreate(generics.ListCreateAPIView):
    """
    Прохождение материалов клиентом
    """

    queryset = MaterialPassing.objects.all()
    serializer_class = MaterialPassingSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    filterset_fields = (
        'id',
        'material',
        'status',
    )

    def get_queryset(self):
        return MaterialPassing.objects.filter(
            user=self.request.user,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        result = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        material = Material.objects.get(id=result.data.get('material'))

        if material.parent and result.data.get('status') == 1:
                MaterialPassing.objects.create(material=material.parent, user=self.request.user,
                                               status=result.data.get('status'))

        return result

class MaterialPassingListAll(generics.ListAPIView):
    """
    Прохождение материалов всех клиентов
    """

    queryset = MaterialPassing.objects.all()
    serializer_class = MaterialPassingSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    filterset_fields = (
        'id',
        'material',
        'status',
    )

    def get_queryset(self):
        return MaterialPassing.objects.all()

class MaterialPassingDetail(generics.RetrieveUpdateAPIView):
    """
    Прохождение материалов клиентом
    """

    queryset = MaterialPassing.objects.all()
    serializer_class = MaterialPassingSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    lookup_field = 'id'

    def get_queryset(self):
        return MaterialPassing.objects.filter(
            user=self.request.user,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if instance.material.parent:
            children = instance.material.parent.children.all()
            if children.count() == MaterialPassing.objects.filter(material_id__in=[material.id for material in children], status=2).count():
                mpp = MaterialPassing.objects.filter(material=instance.material.parent).last()
                if mpp:
                    mpp.status = 2
                    mpp.save()


        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class AnswerClientViewSet(ModelViewSet):
    """
    Варианты ответов на вопросы заданий материалов курсов клиента
    """

    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'question',
        'is_true',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        return Answer.objects.filter(
            question__tasks__material__course__users__in=[self.request.user],
            question__tasks__material__course__is_active=True,
        )


class UserCourseSettingsViewSet(generics.ListCreateAPIView):
    """
    Настройки объединяющие курсы и юзеров
    """

    def post(self, request, *args, **kwargs):
        if UserCourseSettings.objects.filter(user_id=request.data.get('user'),
                                             course_id=request.data.get('course')).count() > 0:
            raise DuplicateRecording()
        return self.create(request, *args, **kwargs)

    queryset = UserCourseSettings.objects.all()
    serializer_class = UserCourseSettingsSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    http_method_names = ['get', 'post']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'course',
        'user',
    )

class CuratorUserCourseSettingsViewSet(UserCourseSettingsViewSet):
    """
    Настройки объединяющие курсы и юзеров для куратора
    """

    permission_classes = (permissions.IsAuthenticated, IsCurator)


class ClientUserCourseSettingsViewSet(UserCourseSettingsViewSet):
    """
    Настройки объединяющие курсы и юзеров для клиента
    """

    permission_classes = (permissions.IsAuthenticated, IsClient)


class UserCourseSettingsDetail(generics.RetrieveUpdateAPIView):
    """
    Настройки объединяющие курсы и юзеров обновление
    """

    queryset = UserCourseSettings.objects.all()
    serializer_class = UserCourseSettingsDetailSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'
