import json
from math import ceil
from datetime import timedelta

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter
from django.utils import timezone
from django.db.models import Count

from rest_framework import filters
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.generics import UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from backend.api_v1.permissions import (
    IsModerator,
    IsAdministrator,
    IsClient,
    ClientTime,
    IsCurator,
    is_administrator,
    is_moderator
)
from backend.api_v1.utils import response_success, response_error
from backend.constants import INVALID_DATA, ALREADY_CREATED
from backend.courses.models import Course
from backend.users.models import Company, User, UserDayActivity, UserOnlineHistory, UserActivity, UserLogErrors
from backend.users.serializers import (
    CompanySerializer,
    MassUsersSerializer,
    UserSerializer,
    CommonUserSerializer,
    CuratorUserSerializer,
    UpdateUserSerializer,
    ChangePasswordSerializer,
    OwnChangePasswordSerializer,
    UserDayActivitySerializer,
    UserActivityDetailsSerializer,
    CourseClientADSerializer,
    ClientUserSerializer,
    UserOnlineHistorySerializer,
    SingleUserSerializer,
    UserLogErrorsSerializer
    )
from backend.courses.models import UserCourseSettings


class CompanyListCreate(generics.ListCreateAPIView):
    """
    Компании
    """
    serializer_class = CompanySerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ('title', 'created', 'id')
    ordering_fields = '__all__'

    def get_queryset(self):
        user = self.request.user
        qs = Company.objects.prefetch_related().with_annotations()
        if user.is_moderator:
            qs = qs.filter(
                Q(company_users__courses__moderators=user) |
                Q(company_users__courses__author=user)
            ).distinct()
        return qs


class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Компании
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        qs = Company.objects.all()
        if user.is_moderator:
            qs = qs.filter(
                Q(company_users__courses__moderators=user) |
                Q(company_users__courses__author=user)
            ).distinct()
        return qs


class MassUsersCreation(generics.GenericAPIView):
    """
    Массовое добавление пользователей, должно быть заполнено только одно из полей
    """
    serializer_class = MassUsersSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        file_users = request.FILES.get('file_users')
        if serializer.is_valid():
            created, message, result_list, code = serializer.create(
                serializer.data,
                file_users
            )

            if created:
                res = json.dumps([
                    'id: {}, username: {}'.format(
                        user.id,
                        user.username
                    ) for user in result_list
                ])

                if serializer.data.get('course_id'):
                    for user in result_list:
                        UserCourseSettings.objects.create(user=user, course_id=serializer.data.get('course_id'),
                                                    start_course=user.start_course,
                                                    end_course=user.end_course)

                return response_success(code, message, res, status.HTTP_201_CREATED)
            else:
                return response_error(code, message, {'already_exist': result_list}, status.HTTP_400_BAD_REQUEST)
        return response_error(INVALID_DATA, 'invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)

class RegisterNewUser(generics.GenericAPIView):
    """
    Регистрация нового пользователя
    """
    serializer_class = SingleUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            created, message, res, code = serializer.register(
                serializer.data,
            )
            return response_success(code, message, res, status.HTTP_201_CREATED)
        else:
            username = username=serializer.data.get('username')
            try:
                user_exists = User.objects.get(username=username)
            except:
                return response_error(INVALID_DATA, 'Проверьте правильность заполнения полей', serializer.errors, status.HTTP_400_BAD_REQUEST)
        if user_exists:
            return response_error(ALREADY_CREATED, f'Пользователь с ником {username} уже существует', 'user exists', status.HTTP_400_BAD_REQUEST)

        return response_error(INVALID_DATA, 'invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)

class SingleUserCreation(generics.GenericAPIView):
    """
    Добавление нового пользователя
    """
    serializer_class = SingleUserSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            created, message, res, code = serializer.create(
                serializer.data,
            )
            return response_success(code, message, res, status.HTTP_201_CREATED)
        else:
            username = username=serializer.data.get('username')
            try:
                user_exists = User.objects.get(username=username)
            except:
                return response_error(INVALID_DATA, 'Проверьте правильность заполнения полей', serializer.errors, status.HTTP_400_BAD_REQUEST)
        if user_exists:
            return response_error(ALREADY_CREATED, f'Пользователь с ником {username} уже существует', 'user exists', status.HTTP_400_BAD_REQUEST)

        return response_error(INVALID_DATA, 'invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)

class UsersPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = 'page_size'


class UserListExamsCreate(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = UsersPagination
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = (
        'user_status',
        'company',
        'id',
        'courses__title',
        'courses__id',
    )
    search_fields = [
        'username',
        'first_name',
    ]
    ordering_fields = '__all__'

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated and is_administrator(self.request.user):
            return User.objects.with_select_related().with_prefetch_related().with_last_passing_date().annotate(
                course_count=Count('courses')).filter(
                        passings__task__is_final=True,
                        passings__success_passed=0,
                        passings__is_trial=False,
                        passings__finish_time__isnull=False
                    )
        elif self.request.user and self.request.user.is_authenticated and is_moderator(self.request.user):
            return User.objects.filter(
                Q(courses__author=self.request.user) |
                Q(courses__moderators=self.request.user)
            ).with_select_related().with_prefetch_related().with_last_passing_date().annotate(
                course_count=Count('courses')).filter(
                        passings__task__is_final=True,
                        passings__success_passed=0,
                        passings__is_trial=False,
                        passings__finish_time__isnull=False
                    )

class UserListCreate(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = UsersPagination
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = (
        'user_status',
        'company',
        'id',
        'courses__title',
        'courses__id',
    )
    search_fields = [
        'username',
        'first_name',
    ]
    ordering_fields = '__all__'

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated and is_administrator(self.request.user):
            return User.objects.with_select_related().with_prefetch_related().with_passing_on_check().annotate(
                course_count=Count('courses'))
        elif self.request.user and self.request.user.is_authenticated and is_moderator(self.request.user):
            return User.objects.filter(
                Q(courses__author=self.request.user) |
                Q(courses__moderators=self.request.user)
            ).with_select_related().with_prefetch_related().with_passing_on_check().annotate(
                course_count=Count('courses'))


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Пользователи
    """
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated and is_administrator(self.request.user):
            return User.objects.all()
        elif self.request.user and self.request.user.is_authenticated and is_moderator(self.request.user):
            return User.objects.filter(
                Q(courses__author=self.request.user) |
                Q(courses__moderators=self.request.user)
            )


class UserClientView(APIView):
    """
    Пользователь (клиент)
    """
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)

    def get(self, request, format=None):
        snippets = User.objects.get(
            pk=self.request.user.pk,
        )
        serializer = ClientUserSerializer(snippets)
        return Response(serializer.data)


class ChangePasswordView(UpdateAPIView):
    """
    Изменение пароля клиентов
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = User.objects.get(pk=serializer.data.get('user_id'))
            if user.user_status == User.STATUS_ADMIN:
                return Response(
                    {'user_id': ['user status is not client']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.data.get('password'))
            user.old_password = serializer.data.get('password')
            user.save()
            return Response("success", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnChPasswordSerializer(UpdateAPIView):
    """
    Изменение своего пароля
    """
    serializer_class = OwnChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user.set_password(serializer.data.get('password'))
            user.old_password = serializer.data.get('password')
            user.save()
            return Response("success", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommonUserView(APIView):
    """
    Данные пользователя
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        current_user = User.objects.get(
            pk=self.request.user.pk,
        )
        serializer = CommonUserSerializer(current_user)
        return Response(serializer.data)


class UsersOnlineView(APIView):
    """
    Количество пользователей онлайн

    GET timedelta_mins: integer default=15 Интервал за который фильтруем активных пользователей в минутах.
    """
    permission_classes = (permissions.IsAuthenticated,)
    ONLINE_DELTA_MIN = 15

    def get(self, request):
        delta = request.query_params.get('timedelta_mins', None)
        if delta is None:
            delta = self.ONLINE_DELTA_MIN
        else:
            try:
                delta = int(delta)
            except ValueError:
                return Response("timedelta_mins parameter must be integer", status=status.HTTP_400_BAD_REQUEST)
        count = User.get_online_clients_count(delta)
        return Response({'online_users': count})


class UserOnlineHistoryFilter(FilterSet):
    min_date = DateFilter(field_name="date", lookup_expr='gte')
    max_date = DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = UserOnlineHistory
        fields = ['min_date', 'max_date']


class UserOnlineHistoryViewSet(ReadOnlyModelViewSet):
    """
    Количество активных пользователей за дату
    """
    queryset = UserOnlineHistory.objects.all()
    serializer_class = UserOnlineHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = UserOnlineHistoryFilter

    def get_queryset(self):
        min_d = self.request.query_params.get('min_date', None)
        max_d = self.request.query_params.get('max_date', None)
        qs = self.queryset
        if min_d is None and max_d is None:
            now_d = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            monday_d = now_d - timedelta(days=now_d.weekday())
            qs = qs.filter(date__gte=monday_d)
        return qs


class CuratorUserViewSet(ModelViewSet):
    """
    Получение пользователей для куратора
    """
    serializer_class = CuratorUserSerializer
    permission_classes = (permissions.IsAuthenticated, IsCurator)
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'company',
        'courses',
    )
    ordering_fields = '__all__'

    def get_queryset(self):
        """
        Получаем только активных пользователей курируемых компаний,
        которые записаны хотябы на один курс.
        """
        # return User.objects.with_select_related()
        return User.objects.prefetch_related(
            'days_activity',
            'courses',
            'courses__materials',
        ).select_related(
            'company',
        ).with_annotations().for_curator(self.request.user.curator_company.all()).distinct()


class CuratorUserProgressView(generics.GenericAPIView):
    """
    Прогресс пользователя для куратора
    """
    permission_classes = (permissions.IsAuthenticated, IsCurator)

    def get(self, request, *args, **kwargs):
        user_pk = kwargs.get('pk')
        res = {}
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist as ex:
            res.update({
                'error': str(ex),
            })
            return Response(res, status=status.HTTP_200_OK)

        course = Course.objects.filter(users=user).first()

        all_tasks_count = course.get_all_tasks().count()
        success_task_count = course.get_success_tasks_for_user(user).count()

        all_course_materials_count = course.get_all_materials().count()
        passed_materials_count = course.get_passed_materials_for_user(
            user
        ).count()

        try:
            result = ceil((success_task_count + all_course_materials_count) /
                          (all_tasks_count + passed_materials_count) * 100)
        except ZeroDivisionError:
            result = 0

        res.update({
            'user_id': user_pk,
            'course_id': course.id,
            'progress': result
        })
        return Response(res, status=status.HTTP_200_OK)


class UserDayActivityViewSet(ModelViewSet):
    """
    Пользовательская активность по дням
    """

    queryset = UserDayActivity.objects.all()
    serializer_class = UserDayActivitySerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    http_method_names = ['get']
    ordering_fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'user',
        'day',
        'course_id',
    )


class ClientUserDayActivityViewSet(ModelViewSet):
    """
    Активность по дням клиента
    """

    serializer_class = UserDayActivitySerializer
    permission_classes = (permissions.IsAuthenticated, IsClient, ClientTime)
    http_method_names = ['get']
    ordering_fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'user',
        'day',
        'course_id',
    )

    def get_queryset(self):
        return UserDayActivity.objects.filter(
            user=self.request.user,
        )


class CourseClientADView(generics.GenericAPIView):
    """
    Добавление/удаление клиента на курс
    """
    serializer_class = CourseClientADSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdministrator)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            done, message = serializer.set_course(serializer.data)
            return response_success('', message, '', status.HTTP_201_CREATED)
        return response_error(INVALID_DATA, 'invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserActivityDetailsViewSet(ModelViewSet):
    """
    Пользовательская активность детальная
    """

    queryset = UserActivity.objects.all()
    serializer_class = UserActivityDetailsSerializer
    permission_classes = (permissions.IsAuthenticated, IsModerator)
    http_method_names = ['get']
    ordering_fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'user',
        'course_id',
    )


class UserLogErrorsViewSet(generics.ListCreateAPIView):
    """
    Логирование ошибок для статистики
    """
    queryset = UserLogErrors.objects.all()
    serializer_class = UserLogErrorsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'post']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = (
        'id',
        'user',
    )
