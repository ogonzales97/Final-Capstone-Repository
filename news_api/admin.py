"""Admin configuration for the news_api app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Publisher, Article, Subscription


class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the User model.

    Extends Django's default UserAdmin to include additional fields
    for managing user roles (Reader, Journalist, Editor) and
    subscriptions directly from the admin interface.
    
    :param fieldsets: Tuple of fieldset configurations for
        the admin form
    :type fieldsets: tuple
    :return: Customized admin interface for User model
    :rtype: django.contrib.admin.ModelAdmin
    """

    fieldsets = UserAdmin.fieldsets + (
        (
            "Roles",
            {
                "fields": (
                    "is_reader",
                    "is_journalist",
                    "is_editor",
                )
            },
        ),
        (
            "Subscriptions",
            {
                "fields": (
                    "subscribed_publishers",
                    "subscribed_journalists",
                )
            },
        ),
    )


# Registering models with the admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Subscription)
