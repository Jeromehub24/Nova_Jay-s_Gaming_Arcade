from django.contrib import admin

from .models import Order, OrderItem, Product, Review, Store, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "updated_at")
    search_fields = ("name", "vendor__username")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "platform", "price", "inventory", "is_active")
    list_filter = ("platform", "genre", "is_active")
    search_fields = ("name", "store__name")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "store_name", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "email", "total", "created_at")
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "buyer", "rating", "is_verified", "created_at")

# Register your models here.
