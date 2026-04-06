from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Order, Product, Store, UserProfile


class StorefrontFlowTests(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(username="vendor", password="secret123", email="vendor@example.com")
        self.buyer = User.objects.create_user(username="buyer", password="secret123", email="buyer@example.com")
        UserProfile.objects.create(user=self.vendor, role=UserProfile.VENDOR)
        UserProfile.objects.create(user=self.buyer, role=UserProfile.BUYER)
        self.store = Store.objects.create(
            vendor=self.vendor,
            name="Night Shift Games",
            description="A dark-themed demo store.",
        )
        self.product = Product.objects.create(
            store=self.store,
            name="Forza Horizon 5",
            description="Arcade racing across a huge map.",
            platform=Product.XBOX,
            genre=Product.RACING,
            price=Decimal("39.99"),
            inventory=5,
        )

    def test_signup_creates_profile_role(self):
        response = self.client.post(
            reverse("storefront:signup"),
            {
                "username": "newvendor",
                "email": "newvendor@example.com",
                "role": UserProfile.VENDOR,
                "password1": "strong-pass-123",
                "password2": "strong-pass-123",
            },
        )
        self.assertRedirects(response, reverse("storefront:login"))
        user = User.objects.get(username="newvendor")
        self.assertEqual(user.profile.role, UserProfile.VENDOR)

    def test_buyer_can_add_product_to_cart(self):
        self.client.login(username="buyer", password="secret123")
        response = self.client.post(reverse("storefront:add-to-cart", args=[self.product.pk]))
        self.assertRedirects(response, reverse("storefront:cart"))
        session_cart = self.client.session.get("nova_cart", {})
        self.assertEqual(session_cart[str(self.product.pk)], 1)

    def test_checkout_creates_order_and_sends_invoice_email(self):
        self.client.login(username="buyer", password="secret123")
        self.client.post(reverse("storefront:add-to-cart", args=[self.product.pk]))
        response = self.client.post(
            reverse("storefront:checkout"),
            {"full_name": "Jeremiah Barker", "email": "jeremiah@example.com"},
        )
        order = Order.objects.get()
        self.assertRedirects(response, reverse("storefront:order-detail", args=[order.pk]))
        self.assertEqual(order.total, Decimal("39.99"))
        self.assertEqual(len(mail.outbox), 1)

    def test_platform_media_helpers_match_real_console_links(self):
        self.assertIn("playstation.com", Product(platform=Product.PLAYSTATION).platform_brand_url)
        self.assertIn("xbox.com", Product(platform=Product.XBOX).platform_brand_url)
        self.assertIn("nintendo.com", Product(platform=Product.NINTENDO).platform_brand_url)
        self.assertEqual(Product(platform=Product.PC).platform_image_url, "")
