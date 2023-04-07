from datetime import timedelta

from django.utils.timezone import now
from rest_framework.permissions import BasePermission

from backend.users.models import User


class ClientTime(BasePermission):
    """
    Проверка клиента на временные ограничения
    end_course + 90 дней
    """

    def has_permission(self, request, view):
        try:
            end_course = request.user.end_course + timedelta(days=90)
        except TypeError:
            return False
        else:
            return now().date() <= end_course


class IsClient(BasePermission):
    """
    Проверка клиента
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_status == User.STATUS_CLIENT)


class IsModerator(BasePermission):
    """
    Проверка модератора
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_status <= User.STATUS_MODERATOR)


class IsAdministrator(BasePermission):
    """
    Проверка администратора
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_status == User.STATUS_ADMIN)


class IsCurator(BasePermission):
    """
    Проверка куратора
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_status == User.STATUS_CURATOR)


class NotCurator(BasePermission):
    """
    Проверка все, кроме куратора
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_status < User.STATUS_CURATOR)


def is_moderator(user):
    """
    Проверка модератора
    """

    return user.user_status == User.STATUS_MODERATOR


def is_administrator(user):
    """
    Проверка администратора
    """

    return user.user_status == User.STATUS_ADMIN


def is_curator(user):
    """
    Проверка куратора
    """

    return user.user_status == User.STATUS_CURATOR
