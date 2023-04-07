from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from backend.helpers import is_allowed

schema_view = get_schema_view(
    openapi.Info(
        title='LMS API',
        default_version='v1',
        description='API for LMS project',
        contact=openapi.Contact(email='birukov.system@gmail.com'),
        url='https://api.lk.promrg.ru/api/v1/',
    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/', include('backend.api_v1.urls')),
    path('chat/', include('backend.mess.urls')),
    path('private_media/', is_allowed, name='private_media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
