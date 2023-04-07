from django.db.models import Prefetch, Subquery, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, filters
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from backend.api_v1.permissions import IsCurator
from backend.courses.models import Passing, Course
from backend.users.curator_serializers import CuratorUsersListSerializer, CuratorUserAllActivitySerializer
from backend.users.models import User, UserDayActivity


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = 'page_size'
    # max_page_size = 100


class CuratorUsersListView(ListAPIView):
    """
    Получение пользователей для куратора
    """
    queryset = User.objects.all()
    serializer_class = CuratorUsersListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.IsAuthenticated, IsCurator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ('id', 'company', 'courses',)
    ordering_fields = '__all__'
    search_fields = [
        'username',
        'first_name',
    ]


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
            Prefetch(
                'passings',
                queryset=Passing.objects.filter(
                    task__is_final=True,
                    task__is_active=True,
                    is_trial=False,
                ),
                to_attr='filtered_final_passing'
            ),
            Prefetch(
                'passings',
                queryset=Passing.objects.filter(
                    task__is_final=False,
                    task__is_active=True,
                    is_trial=False,
                ),
                to_attr='filtered_intermediate_passing'
            ),
            Prefetch(
                'courses',
                queryset=Course.objects.with_num_intermediate_tests(),
                to_attr='courses_with_num_intermediate_tests'
            )
        ).select_related(
            'company',
        ).annotate(
            course_title=Subquery(
                Course.objects.filter(
                    users=OuterRef('pk')
                ).values('title')[:1]),
        ).with_annotations().for_curator(self.request.user.curator_company.all()).distinct()


class CuratorUserAllActivityListView(ListAPIView):
    """
    Получение активности пользователей для куратора
    """
    queryset = UserDayActivity.objects.all()
    serializer_class = CuratorUserAllActivitySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.IsAuthenticated, IsCurator)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ('user',)
    ordering_fields = '__all__'

    def get_queryset(self):
        """
        Получаем только активных пользователей курируемых компаний,
        которые записаны хотябы на один курс.
        """
        # return User.objects.with_select_related()
        return UserDayActivity.objects.for_curator(self.request.user.curator_company.all()).distinct()
