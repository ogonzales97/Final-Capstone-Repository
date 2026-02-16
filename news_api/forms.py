"""Forms for the News API application."""
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    """Form for user registration,
    extending Django's built-in UserCreationForm."""
    class Meta:
        """Meta class to specify the model and fields for the SignUpForm."""
        model = User
        fields = ('username', 'email')
