from rest_framework import serializers

from backend.courses.models import Passing


class TestPassingSerializer(serializers.ModelSerializer):
    """
    Сериализатор прохождения тестов для модератора и выше (только для get)
    """

    is_final_task = serializers.ReadOnlyField()

    class Meta:
        model = Passing
        fields = [
            'id',
            'task',
            'is_final_task',
            'user',
            'success_passed',
            'response_rate',  # !!! ~4000 запросов - убрать из запроса is_trial
            'start_time',
            'out_of_time',
            'finish_time',
            'travel_time',
            'retake_seconds',  # !!! ~1000 запросов - для админа убрать из запроса
            'is_trial',
        ]
        read_only_fields = [
            'id',
            'is_final_task',
            'success_passed',
            'response_rate',
            'start_time',
            'finish_time',
            'travel_time',
            'retake_seconds',
        ]


class ClientTestPassingSerializer(serializers.ModelSerializer):
    """
    Сериализатор прохождения тестов для клиента
    """

    is_final_task = serializers.ReadOnlyField()
    task_attempts = serializers.ReadOnlyField()

    class Meta:
        model = Passing
        fields = [
            'id',
            'task',
            'is_final_task',
            'user',
            'success_passed',
            'response_rate',
            'start_time',
            'out_of_time',
            'finish_time',
            'travel_time',
            'task_attempts',
            'retake_seconds',
            'is_trial',
        ]
        read_only_fields = [
            'id',
            'is_final_task',
            'success_passed',
            'response_rate',
            'start_time',
            'finish_time',
            'travel_time',
            'out_of_time',
            'task_attempts',
            'retake_seconds',
        ]


class OutOfTimeTestPassingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для изменения значения поля out_of_time ('Разрешить пересдачу без интервала')
    """

    is_final_task = serializers.ReadOnlyField()

    class Meta:
        model = Passing
        fields = [
            'id',
            'task',
            'is_final_task',
            'user',
            'out_of_time',
            'is_trial',
        ]
        read_only_fields = [
            'id',
            'task',
            'is_final_task',
            'user',
        ]
