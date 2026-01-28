from django.apps import AppConfig


class DjangoFancyReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_fancy_reports'
    verbose_name = 'Django Fancy Reports'

    def ready(self):
        """
        Run autodiscovery when Django starts.
        This discovers all reports decorated with @register across all apps.
        """
        from .utils.autodiscovery import autodiscover
        autodiscover()
