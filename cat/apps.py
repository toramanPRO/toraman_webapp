from django.apps import AppConfig


class CatConfig(AppConfig):
    name = 'cat'

    def ready(self):
        import cat.signals
