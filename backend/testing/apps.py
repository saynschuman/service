from django.apps import AppConfig


class TestingConfig(AppConfig):
    name = 'backend.testing'
    verbose_name = '3. Тестирование'

    def ready(self):
        import backend.testing.signals
