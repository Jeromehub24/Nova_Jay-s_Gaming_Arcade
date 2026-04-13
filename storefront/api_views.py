"""Class-based API views for the storefront app."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_serializers import ProductSerializer, ReviewSerializer, StoreSerializer
from .models import Product, Store
from .services import announce_new_product, announce_new_store, user_is_vendor


class StoreCreateApiView(APIView):
    """Create vendor-owned stores through the API."""

    def post(self, request):
        """Validate permissions and create a store for the current vendor."""
        if not user_is_vendor(request.user):
            return Response(
                {"detail": "Only vendors can create stores."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store = serializer.save(vendor=request.user)
        announce_new_store(store)
        return Response(StoreSerializer(store).data, status=status.HTTP_201_CREATED)


class VendorStoreListApiView(APIView):
    """List the stores owned by a specific vendor."""

    def get(self, request, vendor_id):
        """Return all stores for the vendor ordered alphabetically."""
        stores = Store.objects.filter(vendor_id=vendor_id).order_by("name")
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


class StoreProductListCreateApiView(APIView):
    """Read products for a store or create a new product as that store owner."""

    def get(self, request, store_id):
        """Return all active products for the requested store."""
        store = get_object_or_404(Store, pk=store_id)
        products = store.products.filter(is_active=True).order_by("name")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, store_id):
        """Create a product when the authenticated user owns the store."""
        if not user_is_vendor(request.user):
            return Response(
                {"detail": "Only vendors can add products."},
                status=status.HTTP_403_FORBIDDEN,
            )

        store = get_object_or_404(Store, pk=store_id, vendor=request.user)
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(store=store)
        announce_new_product(product)
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


class ProductReviewListApiView(APIView):
    """Return the buyer reviews attached to a product."""

    def get(self, request, product_id):
        """Fetch active product reviews together with buyer usernames."""
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        reviews = product.reviews.select_related("buyer").all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
