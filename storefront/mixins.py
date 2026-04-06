from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from .models import Product, Store
from .services import user_is_buyer, user_is_vendor


class VendorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not user_is_vendor(request.user):
            messages.error(request, "Vendor access is required for that page.")
            return redirect("storefront:dashboard")
        return super().dispatch(request, *args, **kwargs)


class BuyerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not user_is_buyer(request.user):
            messages.error(request, "Buyer access is required for that page.")
            return redirect("storefront:dashboard")
        return super().dispatch(request, *args, **kwargs)


class OwnedStoreQuerysetMixin:
    def get_queryset(self):
        return Store.objects.filter(vendor=self.request.user)


class OwnedProductQuerysetMixin:
    def get_queryset(self):
        return Product.objects.filter(store__vendor=self.request.user).select_related("store")
