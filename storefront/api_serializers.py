from rest_framework import serializers

from .models import Product, Review, Store


class StoreSerializer(serializers.ModelSerializer):
    vendor_id = serializers.IntegerField(source="vendor.id", read_only=True)
    vendor_username = serializers.CharField(source="vendor.username", read_only=True)

    class Meta:
        model = Store
        fields = (
            "id",
            "vendor_id",
            "vendor_username",
            "name",
            "description",
            "logo_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "vendor_id", "vendor_username", "created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    store_id = serializers.IntegerField(source="store.id", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "store_id",
            "store_name",
            "name",
            "description",
            "platform",
            "genre",
            "price",
            "inventory",
            "image_url",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "store_id", "store_name", "created_at", "updated_at")


class ReviewSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source="buyer.username", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "buyer_username",
            "rating",
            "comment",
            "is_verified",
            "created_at",
        )
        read_only_fields = ("id", "buyer_username", "is_verified", "created_at")
