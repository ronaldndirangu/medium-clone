from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """
    This class contains a custom app_config for triggering
    profile creatin on user registration
    """

    name = 'authors.apps.authentication'
    label = 'authentication'
    verbose_name = 'Authentication'

    def ready(self):
        import authors.apps.authentication.signals


default_app_config = 'authors.apps.authentication.AuthAppConfig'
