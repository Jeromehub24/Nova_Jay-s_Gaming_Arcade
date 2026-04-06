from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_serializers import ProductSerializer, ReviewSerializer, StoreSerializer
from .models import Product, Store
from .services import announce_new_product, announce_new_store, user_is_vendor


class StoreCreateApiView(APIView):
    def post(self, request):
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
    def get(self, request, vendor_id):
        stores = Store.objects.filter(vendor_id=vendor_id).order_by("name")
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


class StoreProductListCreateApiView(APIView):
    def get(self, request, store_id):
        store = get_object_or_404(Store, pk=store_id)
        products = store.products.filter(is_active=True).order_by("name")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, store_id):
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
    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        reviews = product.reviews.select_related("buyer").all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
