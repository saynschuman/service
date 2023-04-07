import os
import re
from datetime import datetime

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from backend.constants import USERS_CREATE, PARSE_ERROR, ALREADY_CREATED, INVALID_DATA
from backend.courses.models import Course
from backend.users.models import User, Company


def file_validator(file):
    """
    Валидатор расширения и mime типа файла

    :param file: файл
    :return: или ValidationError с описанием или входящий файл
    """

    # READ_SIZE = 5 * (1024 * 1024)  # 5MB
    # detected_type = magic.from_buffer(file_users.read(READ_SIZE), mime=True)
    root, extension = os.path.splitext(file.name.lower())
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ext = '.xlsx'
    # if detected_type != mime_type or extension != ext:
    if extension != ext:
        raise serializers.ValidationError(f'Файл должен быть с расширением <{ext}> и mime type <{mime_type}>')
    return file


def creat_users(text, course_id=None, design=None):
    """
    Создание пользователей из текстового представления
    """
    status = True
    result_list = []
    code = USERS_CREATE
    course = None
    des = design or User.DEFAULT_DESIGN

    if course_id:
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            status = False
            message = f'Курс с ID <{course_id}> не существует'
            code = INVALID_DATA
            return status, message, result_list, code

    try:
        user_list = [usr.strip() for usr in re.split('\d+\.', text) if usr]
        fin_list = [user_data.split('\n') for user_data in user_list]
        names = [name[1].strip() for name in fin_list]
    except Exception as ex:
        status = False
        message = f'{type(ex)}: {ex.__str__()}'
        code = PARSE_ERROR
        return status, message, result_list, code
    else:

        # Проверка на уже существующих пользователей
        old_users = []
        for name in names:
            try:
                User.objects.get(username=name)
            except User.DoesNotExist:
                pass
            else:
                old_users.append(name)
        if old_users:
            status = False
            message = f'Пользователи с ником <{", ".join(old_users)}> уже существуют'
            code = ALREADY_CREATED
            result_list = old_users
            return status, message, result_list, code

        try:
            objects = []
            for name, login, password, company, start_course, end_course in fin_list:
                real_company, created = Company.objects.get_or_create(title=company.strip())

                start_date = datetime.strptime(start_course.strip(), "%Y-%m-%d %H:%M:%S").date()
                end_date = datetime.strptime(end_course.strip(), "%Y-%m-%d %H:%M:%S").date()

                objects.append(
                    User(
                        first_name=name.strip(),
                        username=login.strip(),
                        password=make_password(password.strip()),
                        old_password=password.strip(),
                        company=real_company,
                        start_course=start_date,
                        end_course=end_date,
                        design=des,
                    )
                )
            if objects:
                result_list = User.objects.bulk_create(objects)
            if course:
                course.users.add(*result_list)
            message = f'Созданы пользователи: {names}'
        except Exception as ex:
            status = False
            message = f'{type(ex)}: {ex.__str__()}'
            code = PARSE_ERROR
    return status, message, result_list, code
