"""Reusable access-control mixins for storefront class-based views."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from .models import Product, Store
from .services import user_is_buyer, user_is_vendor


class VendorRequiredMixin(LoginRequiredMixin):
    """Allow access only to authenticated vendor accounts."""

    def dispatch(self, request, *args, **kwargs):
        """Redirect non-vendors back to the dashboard with a message."""
        if not user_is_vendor(request.user):
            messages.error(request, "Vendor access is required for that page.")
            return redirect("storefront:dashboard")
        return super().dispatch(request, *args, **kwargs)


class BuyerRequiredMixin(LoginRequiredMixin):
    """Allow access only to authenticated buyer accounts."""

    def dispatch(self, request, *args, **kwargs):
        """Redirect non-buyers back to the dashboard with a message."""
        if not user_is_buyer(request.user):
            messages.error(request, "Buyer access is required for that page.")
            return redirect("storefront:dashboard")
        return super().dispatch(request, *args, **kwargs)


class OwnedStoreQuerysetMixin:
    """Limit object lookups to stores owned by the current vendor."""

    def get_queryset(self):
        """Return only stores that belong to the logged-in vendor."""
        return Store.objects.filter(vendor=self.request.user)


class OwnedProductQuerysetMixin:
    """Limit object lookups to products owned by the current vendor."""

    def get_queryset(self):
        """Return only products sold by the logged-in vendor."""
        return Product.objects.filter(store__vendor=self.request.user).select_related("store")
