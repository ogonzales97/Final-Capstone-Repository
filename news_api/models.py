"""Defines custom user model for the news application."""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    # Defining the roles
    is_reader = models.BooleanField(default=False)
    is_journalist = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)

    # Reader-specific data (subscribing to other users)
    subscribed_publishers = models.ManyToManyField('Publisher', blank=True, related_name='subscribed_readers')
    subscribed_journalists = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='journalist_subscribers')

    def save(self, *args, **kwargs):
        """Ensure a user doesn't have Reader subscriptions if they are a Journalist."""
        if self.is_journalist or self.is_editor:
            if self.pk:  # If the user already exists
                self.subscribed_publishers.clear()
                self.subscribed_journalists.clear()
        super().save(*args, **kwargs)


class Publisher(models.Model):
    """Model representing a news publisher."""
    name = models.CharField(max_length=255)
    # Linking editors and journalists to a publisher
    editors = models.ManyToManyField(User, related_name='managed_publishers', limit_choices_to={'is_editor': True})
    journalists = models.ManyToManyField(User, related_name='affiliated_publishers', limit_choices_to={'is_journalist': True})

    def __str__(self):
        return self.name


class Article(models.Model):
    """Model representing a news article."""
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('newsletter', 'Newsletter'),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='article')

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_journalist': True})
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='articles')
    published_at = models.DateTimeField(null=True, blank=True)
    reader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='read_articles')

    # Approval status managed by editors
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Subscription(models.Model):
    """Model representing a subscription of a reader to a publisher or journalist."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE, null=True, blank=True)
    journalist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscribers', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class to enforce unique subscriptions."""
        # Ensure a user can't subscribe to the same publisher or journalist multiple times
        unique_together = [('user', 'publisher'), ('user', 'journalist')]

    def __str__(self):
        pub_name = self.publisher.name if self.publisher else "No Publisher"
        return f"{self.user.username} -> {pub_name}"
