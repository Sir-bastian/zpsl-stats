from django.apps import AppConfig

class StatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stats'

    def ready(self):
        import stats.signals 
        # This ensures that the signal handlers are connected when the app is ready, preventing issues with circular imports.