from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'
    verbose_name = 'Каталог услуг'

    def ready(self):
        import services.signals  # noqa: F401
