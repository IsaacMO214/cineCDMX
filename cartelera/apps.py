from django.apps import AppConfig


class CarteleraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cartelera'

    def ready(self):
        import cartelera.signals 
