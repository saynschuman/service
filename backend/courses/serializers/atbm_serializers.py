from rest_framework import serializers

from backend.courses.models import Answer, MaterialPassing, Tag, Bookmark


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class MaterialPassingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialPassing
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'tag', 'created')


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('id', 'material', 'course', 'user', 'title', 'page')
        read_only_fields = ('course',)
