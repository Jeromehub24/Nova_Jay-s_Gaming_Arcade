"""Template context helpers shared across every storefront page."""

from .services import get_cart_count, get_user_role


def storefront_context(request):
    """Expose the cart badge count and current user role to templates."""
    return {
        "cart_count": get_cart_count(request),
        "user_role": get_user_role(request.user),
    }
