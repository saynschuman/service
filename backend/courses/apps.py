from django.apps import AppConfig


class CoursesConfig(AppConfig):
    name = 'backend.courses'
    verbose_name = '2. Курсы'

    def ready(self):
        import backend.courses.signals
