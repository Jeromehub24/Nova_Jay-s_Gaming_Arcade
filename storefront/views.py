"""HTML views for browsing, managing, and purchasing storefront content."""

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import CheckoutForm, ProductForm, ReviewForm, SignUpForm, StoreForm
from .mixins import (
    BuyerRequiredMixin,
    OwnedProductQuerysetMixin,
    OwnedStoreQuerysetMixin,
    VendorRequiredMixin,
)
from .models import Order, OrderItem, Product, Review, Store
from .services import (
    add_product_to_cart,
    announce_new_product,
    announce_new_store,
    buyer_has_purchased_product,
    create_order_from_cart,
    get_cart_items,
    get_cart_total,
    remove_product_from_cart,
    update_cart_item,
    user_is_buyer,
    user_is_vendor,
)


class HomeView(TemplateView):
    """Render the storefront landing page with featured content."""

    template_name = "storefront/home.html"

    def get_context_data(self, **kwargs):
        """Load featured catalog content and summary statistics."""
        context = super().get_context_data(**kwargs)
        context["featured_products"] = Product.objects.filter(is_active=True).select_related("store")[:8]
        context["featured_stores"] = Store.objects.annotate(product_total=Count("products"))[:4]
        context["platform_spotlights"] = Product.platform_spotlights()
        context["stats"] = {
            "stores": Store.objects.count(),
            "products": Product.objects.filter(is_active=True).count(),
            "vendors": Store.objects.values("vendor").distinct().count(),
        }
        return context


class SignUpView(CreateView):
    """Register a new buyer or vendor account."""

    form_class = SignUpForm
    template_name = "storefront/signup.html"
    success_url = reverse_lazy("storefront:login")

    def form_valid(self, form):
        """Show a success message after a valid signup."""
        messages.success(self.request, "Account created. You can log in now.")
        return super().form_valid(form)


class StorefrontLoginView(LoginView):
    """Render the storefront login screen."""

    template_name = "registration/login.html"
    redirect_authenticated_user = True


class StorefrontLogoutView(LogoutView):
    """Log the current user out and return them to the homepage."""

    next_page = reverse_lazy("storefront:home")


class DashboardView(View):
    """Route authenticated users to the correct role-specific dashboard."""

    def get(self, request):
        """Redirect anonymous users to login and others to their dashboard."""
        if not request.user.is_authenticated:
            return redirect("storefront:login")
        if user_is_vendor(request.user):
            return VendorDashboardView.as_view()(request)
        return BuyerDashboardView.as_view()(request)


class VendorDashboardView(VendorRequiredMixin, TemplateView):
    """Show vendor-specific stores, products, and summary statistics."""

    template_name = "storefront/dashboard.html"

    def get_context_data(self, **kwargs):
        """Return the vendor dashboard context."""
        context = super().get_context_data(**kwargs)
        stores = Store.objects.filter(vendor=self.request.user)
        products = Product.objects.filter(store__vendor=self.request.user).select_related("store")
        context["dashboard_mode"] = "vendor"
        context["stores"] = stores
        context["products"] = products
        context["stats"] = {
            "stores": stores.count(),
            "products": products.count(),
            "active_products": products.filter(is_active=True).count(),
            "reviews": Review.objects.filter(product__store__vendor=self.request.user).count(),
        }
        return context


class BuyerDashboardView(BuyerRequiredMixin, TemplateView):
    """Show buyer-specific orders and purchase statistics."""

    template_name = "storefront/dashboard.html"

    def get_context_data(self, **kwargs):
        """Return the buyer dashboard context."""
        context = super().get_context_data(**kwargs)
        orders = Order.objects.filter(buyer=self.request.user).prefetch_related("items")
        context["dashboard_mode"] = "buyer"
        context["orders"] = orders
        context["stats"] = {
            "orders": orders.count(),
            "reviews": Review.objects.filter(buyer=self.request.user).count(),
            "products_bought": OrderItem.objects.filter(order__buyer=self.request.user).count(),
        }
        return context


class ProductListView(ListView):
    """List active products with optional search and platform filters."""

    model = Product
    template_name = "storefront/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        """Filter active products by query string and platform."""
        queryset = Product.objects.filter(is_active=True).select_related("store")
        search = self.request.GET.get("q", "").strip()
        platform = self.request.GET.get("platform", "").strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        if platform:
            queryset = queryset.filter(platform=platform)
        return queryset

    def get_context_data(self, **kwargs):
        """Expose filter state back to the product listing template."""
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["active_platform"] = self.request.GET.get("platform", "").strip()
        context["platform_choices"] = Product.PLATFORM_CHOICES
        return context


class ProductDetailView(DetailView):
    """Display a single product and its buyer reviews."""

    model = Product
    template_name = "storefront/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        """Load store and buyer relationships used by the detail page."""
        return Product.objects.select_related("store", "store__vendor").prefetch_related("reviews__buyer")

    def get_context_data(self, **kwargs):
        """Attach the review form and review permissions to the template."""
        context = super().get_context_data(**kwargs)
        context["review_form"] = ReviewForm()
        context["can_review"] = self.request.user.is_authenticated and user_is_buyer(self.request.user)
        return context


class StoreListView(ListView):
    """List all stores together with product counts."""

    model = Store
    template_name = "storefront/store_list.html"
    context_object_name = "stores"

    def get_queryset(self):
        """Annotate stores with the number of attached products."""
        return Store.objects.annotate(product_total=Count("products"))


class StoreDetailView(DetailView):
    """Display a single store and its active products."""

    model = Store
    template_name = "storefront/store_detail.html"
    context_object_name = "store"

    def get_context_data(self, **kwargs):
        """Add the store's active products to the template context."""
        context = super().get_context_data(**kwargs)
        context["products"] = self.object.products.filter(is_active=True)
        return context


class StoreCreateView(VendorRequiredMixin, CreateView):
    """Allow vendors to create a new store."""

    form_class = StoreForm
    template_name = "storefront/store_form.html"

    def form_valid(self, form):
        """Assign ownership, save the store, and announce it."""
        form.instance.vendor = self.request.user
        messages.success(self.request, "Store created.")
        response = super().form_valid(form)
        announce_new_store(self.object)
        return response


class StoreUpdateView(VendorRequiredMixin, OwnedStoreQuerysetMixin, UpdateView):
    """Allow vendors to update one of their stores."""

    form_class = StoreForm
    template_name = "storefront/store_form.html"
    context_object_name = "store"

    def form_valid(self, form):
        """Show a success message after the store is updated."""
        messages.success(self.request, "Store updated.")
        return super().form_valid(form)


class StoreDeleteView(VendorRequiredMixin, OwnedStoreQuerysetMixin, DeleteView):
    """Allow vendors to delete one of their stores."""

    template_name = "storefront/store_confirm_delete.html"
    context_object_name = "store"
    success_url = reverse_lazy("storefront:dashboard")

    def form_valid(self, form):
        """Show a success message after the store is deleted."""
        messages.success(self.request, "Store deleted.")
        return super().form_valid(form)


class ProductCreateView(VendorRequiredMixin, CreateView):
    """Allow vendors to add a new product to one of their stores."""

    form_class = ProductForm
    template_name = "storefront/product_form.html"

    def get_form_kwargs(self):
        """Pass the current user so store choices can be filtered."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Save the product, show feedback, and announce it."""
        messages.success(self.request, "Product added to your store.")
        response = super().form_valid(form)
        announce_new_product(self.object)
        return response


class ProductUpdateView(VendorRequiredMixin, OwnedProductQuerysetMixin, UpdateView):
    """Allow vendors to edit one of their existing products."""

    form_class = ProductForm
    template_name = "storefront/product_form.html"
    context_object_name = "product"

    def get_form_kwargs(self):
        """Pass the current user so store choices remain restricted."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Show a success message after the product is updated."""
        messages.success(self.request, "Product updated.")
        return super().form_valid(form)


class ProductDeleteView(VendorRequiredMixin, OwnedProductQuerysetMixin, DeleteView):
    """Allow vendors to remove one of their products."""

    template_name = "storefront/product_confirm_delete.html"
    context_object_name = "product"
    success_url = reverse_lazy("storefront:dashboard")

    def form_valid(self, form):
        """Show a success message after the product is deleted."""
        messages.success(self.request, "Product removed.")
        return super().form_valid(form)


class AddToCartView(BuyerRequiredMixin, View):
    """Add a product to the buyer's session cart."""

    def post(self, request, pk):
        """Validate stock and append the product to the cart."""
        product = get_object_or_404(Product, pk=pk, is_active=True)
        if not product.is_in_stock:
            messages.error(request, "That product is out of stock right now.")
            return redirect(product)
        add_product_to_cart(request, product.id)
        messages.success(request, f'"{product.name}" was added to your cart.')
        next_url = request.POST.get("next")
        return HttpResponseRedirect(next_url or reverse("storefront:cart"))


class CartView(BuyerRequiredMixin, TemplateView):
    """Render the buyer's current session cart."""

    template_name = "storefront/cart.html"

    def get_context_data(self, **kwargs):
        """Expose cart items and totals to the cart template."""
        context = super().get_context_data(**kwargs)
        context["cart_items"] = get_cart_items(self.request)
        context["cart_total"] = get_cart_total(self.request)
        return context


class UpdateCartView(BuyerRequiredMixin, View):
    """Update the quantity for a product already in the cart."""

    def post(self, request, pk):
        """Validate the requested quantity and persist the new value."""
        product = get_object_or_404(Product, pk=pk, is_active=True)
        try:
            quantity = int(request.POST.get("quantity", "1"))
        except (TypeError, ValueError):
            messages.error(request, "Enter a valid quantity.")
            return redirect("storefront:cart")

        if quantity > product.inventory:
            messages.error(request, "That quantity is higher than the stock available.")
            return redirect("storefront:cart")

        update_cart_item(request, product.id, quantity)
        messages.success(request, "Cart updated.")
        return redirect("storefront:cart")


class RemoveFromCartView(BuyerRequiredMixin, View):
    """Remove a product from the buyer's cart."""

    def post(self, request, pk):
        """Delete the requested product from the cart."""
        remove_product_from_cart(request, pk)
        messages.success(request, "Item removed from cart.")
        return redirect("storefront:cart")


class CheckoutView(BuyerRequiredMixin, FormView):
    """Collect checkout details and convert the cart into an order."""

    template_name = "storefront/checkout.html"
    form_class = CheckoutForm

    def get_initial(self):
        """Pre-fill the checkout form from the authenticated user."""
        initial = super().get_initial()
        initial["email"] = self.request.user.email
        initial["full_name"] = self.request.user.get_full_name() or self.request.user.username
        return initial

    def form_valid(self, form):
        """Create the order or return the buyer to the cart on failure."""
        try:
            order = create_order_from_cart(
                request=self.request,
                buyer=self.request.user,
                full_name=form.cleaned_data["full_name"],
                email=form.cleaned_data["email"],
            )
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return redirect("storefront:cart")

        messages.success(self.request, "Checkout complete. Your invoice email was sent.")
        return redirect(order)

    def get_context_data(self, **kwargs):
        """Expose cart items and totals during checkout."""
        context = super().get_context_data(**kwargs)
        context["cart_items"] = get_cart_items(self.request)
        context["cart_total"] = get_cart_total(self.request)
        return context


class OrderDetailView(BuyerRequiredMixin, DetailView):
    """Display a single order that belongs to the current buyer."""

    template_name = "storefront/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        """Limit order lookups to the authenticated buyer."""
        return Order.objects.filter(buyer=self.request.user).prefetch_related("items")


class CreateReviewView(BuyerRequiredMixin, View):
    """Create or update the buyer's review for a product."""

    def post(self, request, pk):
        """Persist the review and mark it verified when the buyer purchased."""
        product = get_object_or_404(Product, pk=pk, is_active=True)
        form = ReviewForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please fix the review form errors.")
            return redirect(product)

        verified = buyer_has_purchased_product(request.user, product)
        Review.objects.update_or_create(
            product=product,
            buyer=request.user,
            defaults={
                "rating": form.cleaned_data["rating"],
                "comment": form.cleaned_data["comment"],
                "is_verified": verified,
            },
        )
        messages.success(request, "Review saved.")
        return redirect(product)
