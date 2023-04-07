from rest_framework import serializers


class ApiKeySerializer(serializers.Serializer):
    apikey = serializers.CharField(required=True)
