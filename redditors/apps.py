from django.apps import AppConfig


class RedditorsConfig(AppConfig):
    name = 'redditors'
    
    def ready(self):
        import redditors.signals
