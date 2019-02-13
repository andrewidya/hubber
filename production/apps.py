from django.apps import AppConfig


class ProductionConfig(AppConfig):
    name = 'production'
    verbose_name = 'Huber System'

    def ready(self):
       import production.signals
