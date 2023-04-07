from openpyxl import load_workbook
from rest_framework import serializers

from backend.courses.models import Course, Tag, UserCourseSettings
from backend.users.models import User
from backend.users.utils import file_validator, creat_users


class _AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
        )


class _TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'tag',
        )


class CourseClientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для курсов клиента с вложениями автора и тэгов
    """

    author = _AuthorSerializer()
    tag = _TagSerializer(many=True)

    class Meta:
        model = Course
        exclude = (
            'users',
        )


class CourseAdminSerializer(serializers.ModelSerializer):
    """
    Сериализатор для crud курсов для админа
    с добавление клиентов из файла или текстового поля
    """

    text_users = serializers.CharField(required=False, style={'base_template': 'textarea.html'})
    file_users = serializers.FileField(required=False, validators=[file_validator])
    author_name = serializers.ReadOnlyField(source='author.username')
    visit_num = serializers.IntegerField(required=False)
    completed_num = serializers.IntegerField(required=False)

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'description',
            'teacher',
            'author',
            'author_name',
            'moderators',
            'tag',
            'users',
            'created',
            'registered_num',
            'visit_num',
            'completed_num',
            'text_users',
            'file_users',
            'is_active',
            'start_course',
            'end_course',
            't_chat',
            's_chat',
            'g_chat'
        )
        read_only = ['text_users', 'file_users', 'registered_num', 'visit_num', 'completed_num']

    def validate(self, attrs):
        if attrs.get('text_users') and attrs.get('file_users'):
            raise serializers.ValidationError('Заполните только одно из этих полей: text_users, file_users')
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data = self.create_users(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.create_users(validated_data)
        return super().update(instance, validated_data)

    @staticmethod
    def create_users(validated_data):
        txt = ''

        if validated_data.get('text_users'):
            txt = validated_data.get('text_users')
            del validated_data['text_users']

        elif validated_data.get('file_users'):
            wb = load_workbook(filename=validated_data.get('file_users'), read_only=True)
            sheet = wb.active

            for idx, row in enumerate(sheet.rows):

                # Пропускаем первую строку - названия стобцов
                if idx == 0:
                    continue

                for cell in row:
                    if not cell.value:
                        break
                    txt += str(cell.value) + '\n'

            del validated_data['file_users']

        status, message, result_list, code = creat_users(txt)

        if status:
            validated_data['users'] += result_list
        else:
            raise serializers.ValidationError(code)

        return validated_data


class CourseModeratorSerializer(CourseAdminSerializer):
    """
    Сериализатор для crud курсов для модератора
    с добавление клиентов из файла или текстового поля
    автором курса автоматически становится модератор
    """
    visit_num = serializers.IntegerField(required=False)
    completed_num = serializers.IntegerField(required=False)

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'description',
            'moderators',
            'teacher',
            'tag',
            'users',
            'created',
            'registered_num',
            'visit_num',
            'completed_num',
            'text_users',
            'file_users',
            'is_active',
        )
        read_only = ['author', 'text_users', 'file_users', 'registered_num', 'visit_num', 'completed_num']


class _CourseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
        )


class ItemCourseAdminSerializer(CourseAdminSerializer):
    """
    для админа /api/v1/courses/course/{id}/
    """
    users_detail = _CourseUserSerializer(many=True, read_only=True, source='users')

    class Meta(CourseAdminSerializer.Meta):
        fields = (
            'id',
            'title',
            'description',
            'teacher',
            'author',
            'author_name',
            'moderators',
            'tag',
            'users',
            'created',
            'registered_num',
            'visit_num',
            'completed_num',
            'text_users',
            'file_users',
            'is_active',
            'users_detail',
            'start_course',
            'end_course',
            't_chat',
            's_chat',
            'g_chat'
        )


class ItemCourseModeratorSerializer(CourseModeratorSerializer):
    """
    для модератора /api/v1/courses/course/{id}/
    """
    users_detail = _CourseUserSerializer(many=True, read_only=True, source='users')

    class Meta(CourseModeratorSerializer.Meta):
        fields = (
            'id',
            'title',
            'description',
            'moderators',
            'teacher',
            'tag',
            'users',
            'created',
            'registered_num',
            'visit_num',
            'completed_num',
            'text_users',
            'file_users',
            'is_active',
            'users_detail',
            'start_course',
            'end_course',
            't_chat',
            's_chat',
            'g_chat'
        )


class UserCourseSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseSettings
        fields = (
            'id',
            'user',
            'course',
            'start_course',
            'end_course'
        )


class UserCourseSettingsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseSettings
        fields = (
            'start_course',
            'end_course'
        )
