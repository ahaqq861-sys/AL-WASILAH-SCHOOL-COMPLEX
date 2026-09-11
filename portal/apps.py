import os
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_superuser(sender, **kwargs):
    """
    Signal handler to automatically create a default superuser 
    after database migrations are run on Render.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'AdminPassword123!')

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"--- AUTO-SUPERUSER CREATED: {username} ---")


class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'

    def ready(self):
        post_migrate.connect(create_default_superuser, sender=self)