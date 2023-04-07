import os
from datetime import timedelta

from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = 'y9s5^t!*u(g+os4y3=np4$_@-5+)o#d237z8$lqaey#(1=#kfv'
DEBUG = True
ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'backend.urls'
ASGI_APPLICATION = 'backend.routing.application'
SITE_ID = 1
FILE_UPLOAD_PERMISSIONS = 0o644
AUTH_USER_MODEL = 'users.User'
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 1024 * 10  # Максимальный размер для загружаемых файлов 10 Гб
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'backend.courses.apps.CoursesConfig',
    'backend.mess.apps.MessagesConfig',
    'backend.testing.apps.TestingConfig',
    'backend.users.apps.UsersConfig',
    'backend.conference.apps.ConferenceConfig',
    'backend.extra.apps.ExtraConfig',
    'backend.quickauth.apps.QuickloginConfig',
    'backend.notifications.apps.NotificationsConfig',

    'rest_framework',
    'drf_yasg',
    'django_filters',

    'channels',

    'mptt',
    'solo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lms',
        'USER': 'lms_user',
        'PASSWORD': 'lms_password',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

LOGGING = {}

STATIC_URL = '/static_files/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'assets'),)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}
LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "users.serializers.UserSerializer",
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_USER')
SERVER_EMAIL = os.environ.get('EMAIL_USER')
EMAIL_FROM = DEFAULT_FROM_EMAIL
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
ADMINS = [
    ('Alex', os.environ.get('EMAIL_USER')),
    ('Vitaly', 'saynschuman@gmail.com'),
]

# LOGGING = {
#     'version': 1,
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#             'propagate': False,
#         }
#     }
# }

SWAGGER_SETTINGS = {
    # 'DOC_EXPANSION': 'list',
    # 'OPERATIONS_SORTER': 'method',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
}

CELERY_BROKER_URL = "redis://redis:6379/1"
CELERY_RESULT_BACKEND = 'redis://redis:6379/2'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_BEAT_SCHEDULE = {
    'check_clients': {
        'task': 'backend.users.tasks.check_clients',
        'schedule': crontab(minute=30, hour=0),
    },
}

DJANGO_DEVELOPMENT=True
