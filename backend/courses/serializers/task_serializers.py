from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from backend.courses.models import Task, Material

class TaskCopySerializer(serializers.Serializer):
    material_id = serializers.IntegerField(required=True)
    task_id = serializers.IntegerField(required=True)

    def copy(self, validated_data):
        task = get_object_or_404(Task, pk=validated_data.get('task_id'))
        material = get_object_or_404(Material, pk=validated_data.get('material_id'))
        task.material = material
        questions = task.questions.all()
        task.pk = None
        task.save()
        for question in questions:
            question.pk = None
            question.save()
            question.tasks.set([task])
            question.save()
        task.refresh_from_db()
        return task

class CommonTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'material',
            'title',
            'description',
            'text_explanation',
            'prepared_text',
            'travel_time',
            'retake_seconds',
            'passing',
            'attempts',
            'is_necessarily',
            'is_chance',
            'is_mix',
            'is_miss',
            'is_final',
            'is_hidden',
            'rank',
            'trial_attempts',
            'trial_percents',
        ]


class ModeratorTaskSerializer(CommonTaskSerializer):
    """
    Сериализатор тасков материала для модераторов и выше
    """

    class Meta(CommonTaskSerializer.Meta):
        fields = CommonTaskSerializer.Meta.fields + [
            'num_questions',
            'is_active',
        ]
