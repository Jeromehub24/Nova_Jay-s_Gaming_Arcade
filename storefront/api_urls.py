from django.urls import path

from .api_views import (
    ProductReviewListApiView,
    StoreCreateApiView,
    StoreProductListCreateApiView,
    VendorStoreListApiView,
)

app_name = "storefront_api"

urlpatterns = [
    path("stores/", StoreCreateApiView.as_view(), name="store-create"),
    path("vendors/<int:vendor_id>/stores/", VendorStoreListApiView.as_view(), name="vendor-stores"),
    path("stores/<int:store_id>/products/", StoreProductListCreateApiView.as_view(), name="store-products"),
    path("products/<int:product_id>/reviews/", ProductReviewListApiView.as_view(), name="product-reviews"),
]
