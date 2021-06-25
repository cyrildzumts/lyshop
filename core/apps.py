from django.apps import AppConfig
import django
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals
        logger.info(f"Django Started. Version {django.get_version()}")
