from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Product, Review, Store, UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.RadioSelect,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def save(self, commit=True):
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
    class Meta:
        model = Store
        fields = ("name", "description", "logo_url")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class ProductForm(forms.ModelForm):
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
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields["store"].queryset = Store.objects.filter(vendor=user)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell other buyers what stood out."}),
        }


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    email = forms.EmailField()
