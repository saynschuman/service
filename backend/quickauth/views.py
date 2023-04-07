from rest_framework.views import APIView, Response
from rest_framework import status
from backend.quickauth.models import QuickLogin
from backend.quickauth.serializers import QuickLoginSerializer
from rest_framework.generics import UpdateAPIView
from rest_framework import permissions

class QuickloginViews(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        snippets = QuickLogin.objects.first()
        serializer = QuickLoginSerializer(snippets)
        return Response(serializer.data)

class ChangeQuickLogin(UpdateAPIView):
    serializer_class = QuickLoginSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
          obj = QuickLogin.objects.first()
          if not obj:
            obj = QuickLogin.objects.create(
              client_login=serializer.data.get('client_login'),
              curator_login=serializer.data.get('curator_login'),
              moderator_login=serializer.data.get('moderator_login'),
              admin_login=serializer.data.get('admin_login'),
              client_password=serializer.data.get('client_password'),
              curator_password=serializer.data.get('curator_password'),
              moderator_password=serializer.data.get('moderator_password'),
              admin_password=serializer.data.get('admin_password'),
            )
          else:
            QuickLogin.objects.update(
              client_login=serializer.data.get('client_login'),
              curator_login=serializer.data.get('curator_login'),
              moderator_login=serializer.data.get('moderator_login'),
              admin_login=serializer.data.get('admin_login'),
              client_password=serializer.data.get('client_password'),
              curator_password=serializer.data.get('curator_password'),
              moderator_password=serializer.data.get('moderator_password'),
              admin_password=serializer.data.get('admin_password'),
            )

          return Response('success', status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
