from rest_framework import serializers

from .models import (
    UserAnswer,
)


class ModeratorUserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = (
            'id',
            'passing',
            'question',
            'variants',
            'correct_answer',
            'max_points',
            'answer',
            'answers',
            'file',
            'user_points',
            'get_user_points',
            'text',
            'verifier',
        )
        read_only_fields = (
            'id',
            'passing',
            'question',
            'correct_answer',
            'variants',
            'max_points',
            'answer',
            'answers',
            'file',
            'text',
            'get_user_points',
        )


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = (
            'id',
            'passing',
            'question',
            'answer',
            'answers',
            'text',
            'file',
        )
