# inverso_sa/apps.py
from django.apps import AppConfig

class InversoSaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inverso_sa'

    def ready(self):
        import inverso_sa.signals
