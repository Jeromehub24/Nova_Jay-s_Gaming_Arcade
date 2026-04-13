from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from .functions.twitter_client import TweetClient
from .models import Order, OrderItem, Product, Review, UserProfile


CART_SESSION_KEY = "nova_cart"


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserProfile.VENDOR
    profile = getattr(user, "profile", None)
    return profile.role if profile else None


def user_is_vendor(user):
    return get_user_role(user) == UserProfile.VENDOR


def user_is_buyer(user):
    return get_user_role(user) == UserProfile.BUYER


def get_cart(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def add_product_to_cart(request, product_id, quantity=1):
    cart = get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    save_cart(request, cart)


def update_cart_item(request, product_id, quantity):
    cart = get_cart(request)
    key = str(product_id)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity
    save_cart(request, cart)


def remove_product_from_cart(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)


def clear_cart(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True


def get_cart_items(request):
    cart = get_cart(request)
    if not cart:
        return []

    product_map = {
        product.id: product
        for product in Product.objects.filter(id__in=cart.keys(), is_active=True).select_related("store")
    }

    items = []
    for raw_id, quantity in cart.items():
        product = product_map.get(int(raw_id))
        if not product:
            continue
        subtotal = product.price * quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )
    return items


def get_cart_total(request):
    total = Decimal("0.00")
    for item in get_cart_items(request):
        total += item["subtotal"]
    return total


def get_cart_count(request):
    return sum(get_cart(request).values())


def buyer_has_purchased_product(buyer, product):
    return OrderItem.objects.filter(order__buyer=buyer, product=product).exists()


def verify_existing_reviews_for_buyer(buyer, products):
    product_ids = list(
        {
            product.pk
            for product in products
            if getattr(product, "pk", None) is not None
        }
    )
    if not product_ids:
        return 0

    return Review.objects.filter(
        buyer=buyer,
        product_id__in=product_ids,
        is_verified=False,
    ).update(is_verified=True)


def build_invoice_text(order):
    lines = [
        f"Invoice for order #{order.pk}",
        "",
        f"Buyer: {order.full_name}",
        f"Email: {order.email}",
        "",
        "Items:",
    ]
    for item in order.items.all():
        lines.append(
            f"- {item.product_name} from {item.store_name}: "
            f"{item.quantity} x ${item.price} = ${item.subtotal}"
        )
    lines.extend(["", f"Total: ${order.total}", "", "Thanks for shopping at Jay's Gaming."])
    return "\n".join(lines)


def send_invoice_email(order):
    send_mail(
        subject=f"Jay's Gaming invoice #{order.pk}",
        message=build_invoice_text(order),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=False,
    )


@transaction.atomic
def create_order_from_cart(request, buyer, full_name, email):
    cart_items = get_cart_items(request)
    if not cart_items:
        raise ValueError("Your cart is empty.")

    for item in cart_items:
        if item["quantity"] > item["product"].inventory:
            raise ValueError(
                f'"{item["product"].name}" does not have enough stock for that quantity.'
            )

    order = Order.objects.create(
        buyer=buyer,
        full_name=full_name,
        email=email,
        total=Decimal("0.00"),
    )

    running_total = Decimal("0.00")
    purchased_products = []
    for item in cart_items:
        product = item["product"]
        OrderItem.objects.create(
            order=order,
            product=product,
            store_name=product.store.name,
            product_name=product.name,
            price=product.price,
            quantity=item["quantity"],
        )
        product.inventory -= item["quantity"]
        product.save(update_fields=["inventory", "updated_at"])
        running_total += item["subtotal"]
        purchased_products.append(product)

    order.total = running_total
    order.save(update_fields=["total"])
    verify_existing_reviews_for_buyer(buyer, purchased_products)
    send_invoice_email(order)
    clear_cart(request)
    return order


def announce_new_store(store):
    return TweetClient().post_store_created(store)


def announce_new_product(product):
    return TweetClient().post_product_created(product)
