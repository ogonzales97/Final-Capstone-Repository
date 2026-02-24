"""Setup groups and permissions for the News API application."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news_api.models import Article


class Command(BaseCommand):
    """Django management command to create default groups and permissions."""

    help = "Creates default groups and permissions for the News API"

    def handle(self, *args, **options):
        # Create Groups
        journalist_group, _ = Group.objects.get_or_create(name="Journalists")
        editor_group, _ = Group.objects.get_or_create(name="Editors")

        # Get Article Permissions
        content_type = ContentType.objects.get_for_model(Article)
        view_article = Permission.objects.get(
            codename="view_article", content_type=content_type
        )
        add_article = Permission.objects.get(
            codename="add_article", content_type=content_type
        )
        change_article = Permission.objects.get(
            codename="change_article", content_type=content_type
        )

        # Assign Permissions
        # Journalists can view and add articles
        journalist_group.permissions.add(view_article, add_article)

        # Editors can change articles (to approve them)
        editor_group.permissions.add(view_article, change_article)

        self.stdout.write(
            self.style.SUCCESS("Successfully created groups and permissions!")
        )
