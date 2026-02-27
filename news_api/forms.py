"""Forms for the News API application."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    """
    Form for user registration.

    Extends Django's built-in UserCreationForm to include role selection
    (Reader, Journalist, or Editor) during account creation.

    :param role: Choice field for selecting user account type
    :type role: forms.ChoiceField
    :return: Validated form data with username, email, password,
        and role
    :rtype: dict
    """

    ROLE_CHOICES = [
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, required=True, label="Account Type"
    )

    class Meta(UserCreationForm.Meta):
        """
        Meta class for SignUpForm.

        Defines the model and fields to include in the form.
        Extends UserCreationForm.Meta to add email and role fields.
        """
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "role")
