from rest_framework import permissions, status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backend.api_v1.permissions import IsAdministrator
from backend.conference.models import ConferenceSettings
from backend.conference.serializers import ApiKeySerializer


class GetApiKeyView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        snippets = ConferenceSettings.objects.first()
        serializer = ApiKeySerializer(snippets)
        return Response(serializer.data)


class ChangeApiKeyViewSet(ModelViewSet):
    serializer_class = ApiKeySerializer
    permission_classes = (permissions.IsAuthenticated, IsAdministrator)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            obj = ConferenceSettings.objects.first()
            if not obj:
                obj = ConferenceSettings.objects.create(
                    apikey=serializer.data.get('apikey'),
                )
            else:
                obj.apikey = serializer.data.get('apikey')
                obj.save()
            return Response(obj.apikey, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
