from django.apps import AppConfig


class ProductionConfig(AppConfig):
    name = 'production'
    verbose_name = 'Huber System'

    def ready(self):
        pass
        # import production.signals TODO evalute
