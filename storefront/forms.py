"""Forms used by the storefront HTML interface."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Product, Review, Store, UserProfile


class SignUpForm(UserCreationForm):
    """Register a new buyer or vendor account with an email address."""

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.RadioSelect,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def clean_email(self):
        """Reject duplicate email addresses before the user is created."""
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with that email address already exists."
            )
        return email

    def save(self, commit=True):
        """Persist the user record and matching role profile."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"role": self.cleaned_data["role"]},
            )
        return user


class StoreForm(forms.ModelForm):
    """Capture vendor-managed store details."""

    class Meta:
        model = Store
        fields = ("name", "description", "logo_url")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class ProductForm(forms.ModelForm):
    """Create or update storefront products."""

    class Meta:
        model = Product
        fields = (
            "store",
            "name",
            "description",
            "platform",
            "genre",
            "price",
            "inventory",
            "image_url",
            "is_active",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, user=None, **kwargs):
        """Limit store choices to the current vendor when needed."""
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields["store"].queryset = Store.objects.filter(vendor=user)


class ReviewForm(forms.ModelForm):
    """Collect a buyer rating and written product review."""

    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell other buyers what stood out."}),
        }


class CheckoutForm(forms.Form):
    """Capture the checkout identity information for an order."""

    full_name = forms.CharField(max_length=120)
    email = forms.EmailField()
