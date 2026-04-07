from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy

from .views import (
    AddToCartView,
    CartView,
    CheckoutView,
    CreateReviewView,
    DashboardView,
    HomeView,
    OrderDetailView,
    ProductCreateView,
    ProductDeleteView,
    ProductDetailView,
    ProductListView,
    ProductUpdateView,
    RemoveFromCartView,
    SignUpView,
    StoreCreateView,
    StoreDeleteView,
    StoreDetailView,
    StoreListView,
    StoreUpdateView,
    StorefrontLoginView,
    StorefrontLogoutView,
    UpdateCartView,
)

app_name = "storefront"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", StorefrontLoginView.as_view(), name="login"),
    path("logout/", StorefrontLogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.txt",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("storefront:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            # Django's default success URL is non-namespaced, so set it here.
            success_url=reverse_lazy("storefront:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("stores/", StoreListView.as_view(), name="store-list"),
    path("stores/create/", StoreCreateView.as_view(), name="store-create"),
    path("stores/<int:pk>/", StoreDetailView.as_view(), name="store-detail"),
    path("stores/<int:pk>/edit/", StoreUpdateView.as_view(), name="store-update"),
    path("stores/<int:pk>/delete/", StoreDeleteView.as_view(), name="store-delete"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/create/", ProductCreateView.as_view(), name="product-create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product-update"),
    path(
        "products/<int:pk>/delete/",
        ProductDeleteView.as_view(),
        name="product-delete",
    ),
    path("products/<int:pk>/cart/", AddToCartView.as_view(), name="add-to-cart"),
    path("products/<int:pk>/review/", CreateReviewView.as_view(), name="review-create"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/<int:pk>/update/", UpdateCartView.as_view(), name="cart-update"),
    path("cart/<int:pk>/remove/", RemoveFromCartView.as_view(), name="cart-remove"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
