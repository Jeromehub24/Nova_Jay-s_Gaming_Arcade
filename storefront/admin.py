"""Admin registrations for the storefront domain models."""

from django.contrib import admin

from .models import Order, OrderItem, Product, Review, Store, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Display the user-to-role mapping in the Django admin."""

    list_display = ("user", "role")


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """Support vendor store management in the admin site."""

    list_display = ("name", "vendor", "updated_at")
    search_fields = ("name", "vendor__username")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Expose catalog products with useful search and filter controls."""

    list_display = ("name", "store", "platform", "price", "inventory", "is_active")
    list_filter = ("platform", "genre", "is_active")
    search_fields = ("name", "store__name")


class OrderItemInline(admin.TabularInline):
    """Render purchased items inline when viewing an order record."""

    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "store_name", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Show orders together with their purchased line items."""

    list_display = ("id", "buyer", "email", "total", "created_at")
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review moderation and verification overview within the admin site."""

    list_display = ("product", "buyer", "rating", "is_verified", "created_at")
