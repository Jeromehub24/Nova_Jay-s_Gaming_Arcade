"""Database models for users, catalog items, orders, and reviews."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class UserProfile(models.Model):
    """Store the role associated with a Django user account."""

    BUYER = "buyer"
    VENDOR = "vendor"
    ROLE_CHOICES = [
        (BUYER, "Buyer"),
        (VENDOR, "Vendor"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=BUYER)

    def __str__(self):
        """Return a readable representation of the user role."""
        return f"{self.user.username} ({self.role})"


class Store(models.Model):
    """A vendor-owned storefront that groups multiple products."""

    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=120)
    description = models.TextField()
    logo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        """Return the store name for admin and template displays."""
        return self.name

    def get_absolute_url(self):
        """Return the canonical detail page for the store."""
        return reverse("storefront:store-detail", kwargs={"pk": self.pk})


class Product(models.Model):
    """A sellable game or gaming product offered by a store."""

    PLAYSTATION = "playstation"
    XBOX = "xbox"
    NINTENDO = "nintendo"
    PC = "pc"
    MULTI = "multi"
    PLATFORM_CHOICES = [
        (PLAYSTATION, "PlayStation 5"),
        (XBOX, "Xbox Series X"),
        (NINTENDO, "Nintendo Switch OLED"),
        (PC, "PC"),
        (MULTI, "Multi-platform"),
    ]

    # Reused in a few templates so the console links stay consistent.
    PLATFORM_MEDIA = {
        PLAYSTATION: {
            "brand_name": "PlayStation",
            "brand_url": "https://www.playstation.com/en-us/ps5/",
            "image_url": "https://gmedia.playstation.com/is/image/SIEPDC/ps5-product-thumbnail-01-en-14sep21?$facebook$",
            "image_alt": "PlayStation 5 console",
        },
        XBOX: {
            "brand_name": "Xbox",
            "brand_url": "https://www.xbox.com/en-US/consoles/xbox-series-x",
            "image_url": "https://cms-assets.xboxservices.com/assets/37/d2/37d211d0-5c2c-42c6-bb71-ca7492c5e088.png?n=642227_Hero-Gallery-0_C1_857x676.png",
            "image_alt": "Xbox Series X console",
        },
        NINTENDO: {
            "brand_name": "Nintendo",
            "brand_url": "https://www.nintendo.com/us/gaming-systems/switch/oled-model/",
            "image_url": "https://assets.nintendo.com/image/upload/f_auto/q_auto/c_fill,w_800/ncom/en_US/switch/site-design-update/hardware-hero-combo",
            "image_alt": "Nintendo Switch OLED console",
        },
        PC: {
            "brand_name": "PC",
            "brand_url": "",
            "image_url": "",
            "image_alt": "",
        },
        MULTI: {
            "brand_name": "Multi-platform",
            "brand_url": "",
            "image_url": "",
            "image_alt": "",
        },
    }

    ACTION = "action"
    SPORTS = "sports"
    ADVENTURE = "adventure"
    SHOOTER = "shooter"
    RPG = "rpg"
    RACING = "racing"
    INDIE = "indie"
    GENRE_CHOICES = [
        (ACTION, "Action"),
        (SPORTS, "Sports"),
        (ADVENTURE, "Adventure"),
        (SHOOTER, "Shooter"),
        (RPG, "RPG"),
        (RACING, "Racing"),
        (INDIE, "Indie"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=140)
    description = models.TextField()
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES, default=PC)
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, default=ACTION)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    inventory = models.PositiveIntegerField(default=1)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        """Return the product name for human-readable displays."""
        return self.name

    def get_absolute_url(self):
        """Return the canonical detail page for the product."""
        return reverse("storefront:product-detail", kwargs={"pk": self.pk})

    @property
    def is_in_stock(self):
        """Return ``True`` when the product can currently be purchased."""
        return self.inventory > 0 and self.is_active

    @property
    def platform_label(self):
        """Return the display label for the stored platform value."""
        return dict(self.PLATFORM_CHOICES).get(self.platform, self.platform.title())

    @property
    def platform_media(self):
        """Return branding metadata associated with the product platform."""
        return self.PLATFORM_MEDIA.get(self.platform, {})

    @property
    def platform_brand_name(self):
        """Return the headline brand name for the product platform."""
        return self.platform_media.get("brand_name", self.platform_label)

    @property
    def platform_brand_url(self):
        """Return the external brand URL for the product platform."""
        return self.platform_media.get("brand_url", "")

    @property
    def platform_image_url(self):
        """Return the promotional image URL for the product platform."""
        return self.platform_media.get("image_url", "")

    @property
    def platform_image_alt(self):
        """Return the image alt text for the platform promotional image."""
        return self.platform_media.get("image_alt", self.platform_label)

    @classmethod
    def platform_spotlights(cls):
        """Return curated platform spotlight cards for the homepage."""
        return [
            {
                **cls.PLATFORM_MEDIA[cls.PLAYSTATION],
                "copy": "PlayStation 5 games",
            },
            {
                **cls.PLATFORM_MEDIA[cls.XBOX],
                "copy": "Xbox Series X games",
            },
            {
                **cls.PLATFORM_MEDIA[cls.NINTENDO],
                "copy": "Nintendo Switch OLED games",
            },
            {
                **cls.PLATFORM_MEDIA[cls.PC],
                "copy": "PC games",
            },
        ]


class Order(models.Model):
    """A completed checkout transaction for a buyer."""

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Return a readable label for the order."""
        return f"Order #{self.pk} for {self.buyer.username}"

    def get_absolute_url(self):
        """Return the canonical detail page for the order."""
        return reverse("storefront:order-detail", kwargs={"pk": self.pk})


class OrderItem(models.Model):
    """A single purchased product snapshot captured within an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    store_name = models.CharField(max_length=120)
    product_name = models.CharField(max_length=140)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        """Return the stored line subtotal for this purchased item."""
        return self.price * self.quantity


class Review(models.Model):
    """A buyer-authored rating and comment attached to a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("product", "buyer")]

    def __str__(self):
        """Return a readable label for the review."""
        return f"{self.product.name} review by {self.buyer.username}"
