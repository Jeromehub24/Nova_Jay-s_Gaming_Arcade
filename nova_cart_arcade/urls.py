"""Top-level URL routes for the Nova Cart Arcade project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('storefront.api_urls')),
    path('', include('storefront.urls')),
]
