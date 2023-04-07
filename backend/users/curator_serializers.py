from django.contrib.auth import get_user_model
from rest_framework import serializers

from backend.courses.models import Passing, Task, Course
from backend.users.models import Company, UserDayActivity
from backend.users.serializers import _PassingSerializer

User = get_user_model()


class _CpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id',
            'title',
        )


class _TaskCuratorSerializer(serializers.ModelSerializer):
    course_id = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()

    def get_course_id(self, obj):
        return obj.material.course.id

    def get_course_title(self, obj):
        return obj.material.course.title

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'is_final',
            'material',
            'course_id',
            'course_title'
        )


class _PgSerializer(serializers.ModelSerializer):
    task = serializers.SerializerMethodField()

    def get_task(self, obj):
        task = _TaskCuratorSerializer(obj.task, many=False).data
        return task

    class Meta:
        model = Passing
        fields = (
            'created',
            'task',
            'success_passed',
            'is_trial',
            'response_rate',
        )


class _TkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'is_final',
            'material',
        )


class _CsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)

    # num_intermediate_tests = serializers.IntegerField(read_only=True)
    num_intermediate_tests = serializers.SerializerMethodField()
    intermediate_passings = serializers.SerializerMethodField()
    final_passings = serializers.SerializerMethodField()

    def get_final_passings(self, obj):
        if self.user_id:
            return _PassingSerializer(Passing.objects.filter(
                user_id=self.user_id,
                task_id__in=[task.id for task in obj.get_all_tasks()],
                task__is_final=True,
            ), many=True).data
        else:
            return _PassingSerializer(Passing.objects.filter(
                task_id__in=[task.id for task in obj.get_all_tasks()],
                task__is_final=True,
            ), many=True).data

    def get_num_intermediate_tests(self, obj):
        return obj.num_intermediate_tests if obj.num_intermediate_tests < 2 else obj.num_intermediate_tests

    def get_intermediate_passings(self, obj):
        if self.user_id:
            passings = Passing.objects.filter(
                user_id=self.user_id,
                task_id__in=[task.id for task in obj.get_all_tasks()],
                task__is_final=False,
                task__is_active=True,
                is_trial=False,
            )
        else:
            passings = Passing.objects.filter(
                task_id__in=[task.id for task in obj.get_all_tasks()],
                task__is_final=False,
                task__is_active=True,
                is_trial=False,
            )
        s_passings = _PgSerializer(passings, many=True).data
        return s_passings

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'num_intermediate_tests',
            'intermediate_passings',
            'final_passings',
            'start_course',
            'end_course',
            't_chat',
            's_chat',
            'g_chat'
        )


class CuratorUsersListSerializer(serializers.ModelSerializer):
    company = _CpSerializer(read_only=True)
    courses = serializers.SerializerMethodField()
    last_activity = serializers.DateTimeField(read_only=True)
    course_title = serializers.CharField(read_only=True)
    final_passings = _PgSerializer(
        source='filtered_final_passing',
        many=True,
        read_only=True
    )
    intermediate_passings = _PgSerializer(
        source='filtered_intermediate_passing',
        many=True,
        read_only=True
    )
    def get_courses(self, obj):
        return _CsSerializer(obj.courses_with_num_intermediate_tests, many=True, user_id=obj.id).data

    #courses = _CsSerializer(
    #    source='courses_with_num_intermediate_tests',
    #    many=True,
    #    read_only=True
    #)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'company',
            'courses',
            'course_title',
            'start_course',
            'end_course',
            'last_activity',  # аннотировано
            'final_passings',
            'intermediate_passings',
        ]


class CuratorUserAllActivitySerializer(serializers.ModelSerializer):
    human_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserDayActivity
        fields = (
            'user',
            'day',
            'seconds',
            'course_id',
            'human_time',
        )
