import ast

from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from backend.courses.models import Course, Passing, MaterialPassing, Material, Task, UserCourseSettings
from backend.users.models import UserOnlineHistory
from backend.users.utils import file_validator, creat_users
from backend.constants import USERS_CREATE
from backend.users.models import Company, UserDayActivity, UserActivity, UserLogErrors

User = get_user_model()


class _PassingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passing
        fields = (
            'created',
            'task',
            'success_passed',
            'is_trial',
            'response_rate',
        )


class UserDayActivitySerializer(serializers.ModelSerializer):
    """
    Сериализатор пользовательской октивности по дням (только get)
    """

    class Meta:
        model = UserDayActivity
        fields = (
            'id',
            'user',
            'course_id',
            'day',
            'seconds',
            'human_time',
        )


class CompanyForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id',
            'title',
        )


class CourseForUserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        try:
            self.raw_last_test_passings = kwargs.pop('last_test_passings')
        except KeyError:
            pass
        super().__init__(*args, **kwargs)

    last_test_passings = serializers.SerializerMethodField()

    def get_last_test_passings(self, obj):
        result = []
        try:
            for passing in self.raw_last_test_passings:
                if obj.id == passing['course']:
                    result.append(passing)
        except (AttributeError, KeyError):
            pass
        return result

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'description',
            'author',
            'last_test_passings'
        )


class CompanySerializer(serializers.ModelSerializer):
    active_users = serializers.IntegerField(required=False)
    all_users = serializers.IntegerField(required=False)

    class Meta:
        model = Company
        fields = ('id', 'title', 'created', 'active_users', 'all_users')
        read_only = ['active_users', 'all_users']


class _UserPassingSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()

    def get_course(self, obj):
        return obj.task.material.course.id

    class Meta:
        model = Passing
        fields = (
            'id',
            'task',
            'is_final_task',
            'success_passed',
            'response_rate',
            'start_time',
            'finish_time',
            'course'
        )


class UserSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    last_test_passings = serializers.SerializerMethodField()
    on_check = serializers.IntegerField(read_only=True)
    last_passing_dt = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'description',
            'design',
            'webinars',
            'password',
            'old_password',
            'user_status',
            'is_active',
            'company',
            'company_title',
            'curator_company',
            'time_limitation',
            'date_joined',
            'courses',
            'start_course',
            'end_course',
            'teacher_chat',
            'group_chat',
            'tech_chat',
            'on_check',
            'last_passing_dt',
            'last_test_passings',  # !!! ~900 запросов, по запросу на одного пользователя
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
        read_only_fields = (
            'old_password',
            'last_login',
            'date_joined',
            'company_title',
        )

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.old_password = validated_data['password']
        user.save()
        return user

    def get_last_test_passings(self, obj):
        result = {}
        if obj.user_course:
            user_passings = _UserPassingSerializer(
                obj.passings.filter(is_trial=False).prefetch_related(
                    'task'
                ).select_related(
                    'task__material__course'
                ).order_by('task'),
                many=True).data
            for item in user_passings:
                if item['task'] in result:
                    if item['start_time'] > result[item['task']]['start_time']:
                        result[item['task']] = item
                else:
                    result[item['task']] = item
        return result.values()

    def get_courses(self, obj):
        return CourseForUserSerializer(obj.courses.all(), many=True,
                                       last_test_passings=self.get_last_test_passings(obj)).data


class ClientUserSerializer(UserSerializer):
    def get_last_test_passings(self, obj):
        result = {}
        if obj.user_course:
            psgs = obj.passings.prefetch_related(
                'task'
            ).select_related(
                'task__material__course'
            ).filter(
                user=obj,
                task__material__course=obj.user_course,
                is_trial=False,
                task__is_final=True,
            ).order_by('task')
            for item in psgs:
                data = {
                    'id': item.id,
                    'task': item.task.id,
                    'is_final_task': item.is_final_task,
                    'success_passed': item.success_passed,
                    'response_rate': item.response_rate,
                    'start_time': item.start_time,
                    'out_of_time': item.out_of_time,
                    'finish_time': item.finish_time,
                    'travel_time': item.travel_time,
                    'retake_seconds': item.retake_seconds,
                }
                if item.task.id in result:
                    if item.start_time > result[item.task.id]['start_time']:
                        result[item.task.id] = data
                else:
                    result[item.task.id] = data
        return result.values()


class _MaterialPassingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialPassing
        fields = '__all__'


class UpdateUserSerializer(serializers.ModelSerializer):
    courses = CourseForUserSerializer(many=True, read_only=True)
    material_passings = _MaterialPassingSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'description',
            'design',
            'webinars',
            'old_password',
            'user_status',
            'is_active',
            'company',
            'company_title',
            'courses',
            'material_passings',
            'curator_company',
            'time_limitation',
            'start_course',
            'end_course',
            'teacher_chat',
            'group_chat',
            'tech_chat',
        )
        read_only_fields = ('old_password', 'last_login', 'date_joined', 'company_title')


class ChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True)


class OwnChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)


class UserOnlineHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOnlineHistory
        fields = ['date', 'active_clients_count']
        read_only_fields = ['date', 'active_clients_count']


class CommonUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'design',
            'webinars',
            'old_password',
            'user_status',
            'is_active',
            'teacher_chat',
            'group_chat',
            'tech_chat',
        )
        read_only_fields = ('old_password', 'user_status', 'is_active')


class MassUsersSerializer(serializers.Serializer):
    text_users = serializers.CharField(required=False, style={'base_template': 'textarea.html'})
    file_users = serializers.FileField(required=False, validators=[file_validator])
    course_id = serializers.IntegerField(required=False)
    design = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if attrs.get('text_users') and attrs.get('file_users'):
            raise serializers.ValidationError('Заполните только одно из этих полей: text_users, file_users')
        if not attrs.get('text_users') and not attrs.get('file_users'):
            raise serializers.ValidationError('Одно из этих полей должно быть заполнено: text_users, file_users')
        return super().validate(attrs)

    def create(self, validated_data, file_users=None):
        txt = ''

        if validated_data.get('text_users'):
            txt = validated_data.get('text_users')
        elif file_users:
            from openpyxl import load_workbook
            wb = load_workbook(filename=file_users, read_only=True)
            sheet = wb.active

            for idx, row in enumerate(sheet.rows):

                # Пропускаем первую строку - названия стобцов
                if idx == 0:
                    continue

                for cell in row:
                    if not cell.value:
                        break
                    txt += str(cell.value) + '\n'

        return creat_users(txt, validated_data.get('course_id'), validated_data.get('design'))

class SingleUserSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(required=False)
    company_name = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'password',
            'company_name',
            'start_course',
            'end_course',
            'design',
            'course_id',
        )

    def create(self, validated_data):
        data_company = ''
        try:
            validated_data['company_name']
            data_company = validated_data['company_name']
        except:
            print('no company name', validated_data)

        created_company = Company.objects.get_or_create(title=data_company)
        real_company = Company.objects.get(title=created_company[0])
        user = User.objects.create(
            first_name=validated_data["first_name"],
            username=validated_data["username"],
            design=validated_data["design"],
            password=make_password(validated_data["password"].strip()),
            old_password=validated_data["password"],
            company=real_company,
            start_course=validated_data["start_course"],
            end_course=validated_data["end_course"],
        )

        if validated_data["course_id"]:
            course = Course.objects.get(pk=validated_data["course_id"])
            course.users.add(user)
            UserCourseSettings.objects.create(
                user=user,
                course_id=validated_data["course_id"],
                start_course=validated_data["start_course"],
                end_course=validated_data["end_course"],
            )

        return True, f'Пользователь {validated_data["username"]} успешно создан', validated_data, USERS_CREATE

    def register(self, validated_data):
        User.objects.create(
            user_status=0,
            first_name=validated_data["first_name"],
            username=validated_data["username"],
            password=make_password(validated_data["password"].strip()),
        )

        return True, f'Пользователь {validated_data["username"]} успешно создан', validated_data, USERS_CREATE

class _MaterialPassingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialPassing
        fields = (
            'id',
            'material',
            'status',
        )


class _MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = (
            'id',
            'title',
        )


class _CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'description',
            'author',
        )


class _TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'is_final',
        )


class _UserDayActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDayActivity
        fields = (
            'course_id',
            'day',
            'seconds',
            'human_time',
        )


class CuratorUserSerializer(serializers.ModelSerializer):
    company = CompanyForUserSerializer()
    courses = serializers.SerializerMethodField(read_only=True)
    last_activity = serializers.DateTimeField(read_only=True)
    days_activity = _UserDayActivitySerializer(many=True, read_only=True)
    final_passings = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'company',
            'time_limitation',
            'date_joined',
            'courses',  # !!!
            'start_course',
            'end_course',
            'last_activity',
            'days_activity',
            'final_passings',  # !!!
        )

    def get_final_passings(self, obj):
        """
        Попытки прохождения финального тестирования
        """
        return _PassingSerializer(obj.passings.filter(
            task__is_final=True,
        ), many=True).data

    @staticmethod
    def get_tasks(user, material_id):
        """
        Задания для выбранного курса
        Для всех заданий отдаются последние прохождения пользователя
        """
        tasks = _TaskSerializer(Task.objects.filter(
            is_active=True,
            material_id=material_id,
        ), many=True).data
        for task in tasks:
            last_passing = Passing.objects.filter(
                user=user,
                task=task['id'],
                is_trial=False,
            ).last()
            if last_passing:
                task.update({
                    'start_time': last_passing.start_time,
                    'finish_time': last_passing.finish_time,
                    'passing_status': last_passing.success_passed,
                })
        return tasks

    def get_courses(self, obj):
        """
        Для курса отдаем все активные материалы, для всех материалов отдаем статус прохождения пользователем,
        если прохождения нет, то создаем его и статвим статус в STATUS_NOT_STARTED
        """
        courses = _CourseSerializer(obj.courses, many=True).data
        for course in courses:
            materials = _MaterialSerializer(
                Material.objects.filter(
                    course=course['id'],
                    is_active=True,
                ).order_by('rank', 'id'),
                many=True,
            ).data
            for material in materials:
                try:
                    status, _ = MaterialPassing.objects.get_or_create(
                        user=obj,
                        material_id=material['id'],
                        defaults={
                            'status': MaterialPassing.STATUS_NOT_STARTED
                        }
                    )
                except MaterialPassing.MultipleObjectsReturned:
                    status = MaterialPassing.objects.filter(
                        user=obj,
                        material_id=material['id'],
                    ).first()
                material.update({
                    'material_passing_status': status.status,
                    'tasks': self.get_tasks(obj, material['id']),
                })
            course.update({
                'materials': materials,
            })
        return courses


class CourseClientADSerializer(serializers.Serializer):
    """
    Серилизатор для добавления/удаления клиента на курс
    """

    user_id = serializers.IntegerField(min_value=1)
    course_id = serializers.IntegerField(min_value=1)
    action = serializers.ChoiceField(choices=('add', 'del'))

    @staticmethod
    def set_course(validated_data):
        try:
            course = Course.objects.get(pk=validated_data['course_id'])
            user = User.objects.get(pk=validated_data['user_id'])
        except Exception as ex:
            return False, str(ex)
        else:
            if validated_data['action'] == 'add':
                course.users.add(user)
            elif validated_data['action'] == 'del':
                # from backend.courses.models import UserCourseSettings
                # try:
                #     user_course_settings = UserCourseSettings.objects.get(user_id=validated_data['user_id'],
                #                                                           course_id=validated_data['course_id'])
                #     user_course_settings.delete()
                # except ObjectDoesNotExist:
                #     pass
                course.users.remove(user)
        return True, 'user {} {} course {}'.format(user.id, validated_data['action'], course.id)


class UserActivityDetailsSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользовательской октивности детальная (только get)
    """

    payload = serializers.SerializerMethodField(read_only=True)

    def get_payload(self, obj):
        return ast.literal_eval(obj.payload)

    class Meta:
        model = UserActivity
        fields = (
            'id',
            'user',
            'course_id',
            'payload',
        )

class UserLogErrorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLogErrors
        fields = (
            'id',
            'created',
            'user',
            'text'
        )
