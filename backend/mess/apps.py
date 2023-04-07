from django.apps import AppConfig


class MessagesConfig(AppConfig):
    name = 'backend.mess'
    verbose_name = '4. Чат'

    def ready(self):
        import backend.mess.signals
