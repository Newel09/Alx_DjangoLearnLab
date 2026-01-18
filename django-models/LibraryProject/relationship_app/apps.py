from django.apps import AppConfig


class RelationshipAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'relationship_app'
    
    def ready(self):
        """
        Import signals when the app is ready.
        This ensures the signal handlers are registered.
        """
        import relationship_app.signals
