from .services import get_cart_count, get_user_role


def storefront_context(request):
    return {
        "cart_count": get_cart_count(request),
        "user_role": get_user_role(request.user),
    }
