from django.apps import AppConfig


class WwwConfig(AppConfig):
    name = 'www'

    def ready(self):
        import www.signals
