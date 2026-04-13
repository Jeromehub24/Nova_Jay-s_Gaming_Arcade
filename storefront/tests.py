from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase

from .models import Order, OrderItem, Product, Review, Store, UserProfile


class StorefrontFlowTests(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            username="vendor",
            password="secret123",
            email="vendor@example.com",
        )
        self.buyer = User.objects.create_user(
            username="buyer",
            password="secret123",
            email="buyer@example.com",
        )
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

    def test_signup_rejects_duplicate_email_case_insensitively(self):
        response = self.client.post(
            reverse("storefront:signup"),
            {
                "username": "buyerclone",
                "email": "BUYER@EXAMPLE.COM",
                "role": UserProfile.BUYER,
                "password1": "strong-pass-123",
                "password2": "strong-pass-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "An account with that email address already exists.",
        )
        self.assertFalse(User.objects.filter(username="buyerclone").exists())

    def test_email_unique_constraint_blocks_duplicate_addresses(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="buyer_duplicate",
                password="secret123",
                email="buyer@example.com",
            )

    def test_logout_is_rendered_as_post_form(self):
        self.client.login(username="buyer", password="secret123")

        response = self.client.get(reverse("storefront:home"))

        self.assertContains(
            response,
            f'action="{reverse("storefront:logout")}"',
        )
        self.assertContains(response, 'method="post"')

    def test_logout_post_ends_the_session(self):
        self.client.login(username="buyer", password="secret123")

        response = self.client.post(reverse("storefront:logout"))

        self.assertRedirects(response, reverse("storefront:home"))
        dashboard_response = self.client.get(reverse("storefront:dashboard"))
        self.assertEqual(dashboard_response.status_code, 302)

    def test_password_reset_confirm_redirects_to_namespaced_complete_url(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.buyer.pk))
        token = default_token_generator.make_token(self.buyer)
        confirm_url = reverse(
            "storefront:password_reset_confirm",
            kwargs={"uidb64": uidb64, "token": token},
        )

        # Django rewrites the token URL once before it accepts the password POST.
        redirect_response = self.client.get(confirm_url)
        self.assertEqual(redirect_response.status_code, 302)

        response = self.client.post(
            redirect_response.url,
            {
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        # This catches the built-in non-namespaced success URL regression.
        self.assertRedirects(
            response,
            reverse("storefront:password_reset_complete"),
        )
        self.assertTrue(
            self.client.login(
                username="buyer",
                password="new-strong-pass-123",
            )
        )

    def test_buyer_can_add_product_to_cart(self):
        self.client.login(username="buyer", password="secret123")
        response = self.client.post(
            reverse("storefront:add-to-cart", args=[self.product.pk])
        )
        self.assertRedirects(response, reverse("storefront:cart"))
        session_cart = self.client.session.get("nova_cart", {})
        self.assertEqual(session_cart[str(self.product.pk)], 1)

    def test_checkout_creates_order_and_sends_invoice_email(self):
        self.client.login(username="buyer", password="secret123")
        self.client.post(reverse("storefront:add-to-cart", args=[self.product.pk]))
        response = self.client.post(
            reverse("storefront:checkout"),
            {
                "full_name": "Jeremiah Barker",
                "email": "jeremiah@example.com",
            },
        )
        order = Order.objects.get()
        self.assertRedirects(
            response,
            reverse("storefront:order-detail", args=[order.pk]),
        )
        self.assertEqual(order.total, Decimal("39.99"))
        self.assertEqual(len(mail.outbox), 1)

    def test_platform_media_helpers_match_real_console_links(self):
        self.assertIn(
            "playstation.com",
            Product(platform=Product.PLAYSTATION).platform_brand_url,
        )
        self.assertIn(
            "xbox.com",
            Product(platform=Product.XBOX).platform_brand_url,
        )
        self.assertIn(
            "nintendo.com",
            Product(platform=Product.NINTENDO).platform_brand_url,
        )
        self.assertEqual(Product(platform=Product.PC).platform_image_url, "")

    def test_vendor_web_store_create_calls_announcement(self):
        self.client.login(username="vendor", password="secret123")
        with patch("storefront.views.announce_new_store") as announce_mock:
            response = self.client.post(
                reverse("storefront:store-create"),
                {
                    "name": "Side Quest Supply",
                    "description": "A second test store.",
                    "logo_url": "https://example.com/logo.png",
                },
            )

        new_store = Store.objects.get(name="Side Quest Supply")
        self.assertRedirects(
            response,
            reverse("storefront:store-detail", args=[new_store.pk]),
        )
        announce_mock.assert_called_once_with(new_store)

    def test_review_is_marked_verified_after_a_purchase(self):
        Order.objects.create(
            buyer=self.buyer,
            full_name="Jeremiah Barker",
            email="buyer@example.com",
            total=self.product.price,
        )
        order = Order.objects.get()
        OrderItem.objects.create(
            order=order,
            product=self.product,
            store_name=self.store.name,
            product_name=self.product.name,
            price=self.product.price,
            quantity=1,
        )

        self.client.login(username="buyer", password="secret123")
        response = self.client.post(
            reverse("storefront:review-create", args=[self.product.pk]),
            {"rating": 5, "comment": "Loved it."},
        )

        self.assertRedirects(
            response,
            reverse("storefront:product-detail", args=[self.product.pk]),
        )
        review = Review.objects.get(product=self.product, buyer=self.buyer)
        self.assertTrue(review.is_verified)

    def test_checkout_updates_existing_review_to_verified(self):
        review = Review.objects.create(
            product=self.product,
            buyer=self.buyer,
            rating=4,
            comment="Looks fun even before checkout.",
            is_verified=False,
        )

        self.client.login(username="buyer", password="secret123")
        self.client.post(reverse("storefront:add-to-cart", args=[self.product.pk]))
        response = self.client.post(
            reverse("storefront:checkout"),
            {
                "full_name": "Jeremiah Barker",
                "email": "buyer@example.com",
            },
        )

        order = Order.objects.get()
        self.assertRedirects(
            response,
            reverse("storefront:order-detail", args=[order.pk]),
        )
        review.refresh_from_db()
        self.assertTrue(review.is_verified)


class StorefrontApiTests(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            username="vendor_api",
            password="secret123",
            email="vendor_api@example.com",
        )
        self.buyer = User.objects.create_user(
            username="buyer_api",
            password="secret123",
            email="buyer_api@example.com",
        )
        UserProfile.objects.create(user=self.vendor, role=UserProfile.VENDOR)
        UserProfile.objects.create(user=self.buyer, role=UserProfile.BUYER)
        self.store = Store.objects.create(
            vendor=self.vendor,
            name="Controller Corner",
            description="Pads, sticks, and racing wheels.",
        )
        self.product = Product.objects.create(
            store=self.store,
            name="EA Sports FC 26",
            description="Football game with quick matches.",
            platform=Product.PLAYSTATION,
            genre=Product.SPORTS,
            price=Decimal("59.99"),
            inventory=8,
        )

    def test_vendor_can_create_store_with_api(self):
        self.client.login(username="vendor_api", password="secret123")
        with patch("storefront.api_views.announce_new_store") as announce_mock:
            response = self.client.post(
                "/api/stores/",
                {
                    "name": "Arcade Replay",
                    "description": "Retro and new releases.",
                    "logo_url": "https://example.com/replay-logo.png",
                },
                format="json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Store.objects.filter(
                name="Arcade Replay",
                vendor=self.vendor,
            ).exists()
        )
        announce_mock.assert_called_once()

    def test_vendor_can_add_product_with_api(self):
        self.client.login(username="vendor_api", password="secret123")
        with patch("storefront.api_views.announce_new_product") as announce_mock:
            response = self.client.post(
                f"/api/stores/{self.store.pk}/products/",
                {
                    "name": "Halo Infinite",
                    "description": "Shooter with campaign and multiplayer.",
                    "platform": Product.XBOX,
                    "genre": Product.SHOOTER,
                    "price": "49.99",
                    "inventory": 4,
                    "image_url": "https://example.com/halo.png",
                    "is_active": True,
                },
                format="json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Product.objects.filter(
                name="Halo Infinite",
                store=self.store,
            ).exists()
        )
        announce_mock.assert_called_once()

    def test_buyer_can_view_vendor_stores_and_store_products(self):
        self.client.login(username="buyer_api", password="secret123")
        store_response = self.client.get(f"/api/vendors/{self.vendor.pk}/stores/")
        product_response = self.client.get(f"/api/stores/{self.store.pk}/products/")

        self.assertEqual(store_response.status_code, 200)
        self.assertEqual(product_response.status_code, 200)
        self.assertEqual(store_response.data[0]["name"], self.store.name)
        self.assertEqual(product_response.data[0]["name"], self.product.name)

    def test_vendor_can_retrieve_product_reviews_with_api(self):
        self.client.login(username="buyer_api", password="secret123")
        self.product.reviews.create(
            buyer=self.buyer,
            rating=4,
            comment="Pretty fun game night pickup.",
            is_verified=False,
        )
        self.client.logout()

        self.client.login(username="vendor_api", password="secret123")
        response = self.client.get(f"/api/products/{self.product.pk}/reviews/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["comment"], "Pretty fun game night pickup.")
