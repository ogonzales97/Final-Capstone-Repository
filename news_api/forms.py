"""Forms for the News API application."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    """Form for user registration,
    extending Django's built-in UserCreationForm."""

    ROLE_CHOICES = [
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, required=True, label="Account Type"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "role")
