"""App configuration for the storefront Django application."""

from django.apps import AppConfig


class StorefrontConfig(AppConfig):
    """Register the storefront app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "storefront"
