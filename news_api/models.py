"""
Defines the database schema for the news application,
including Users, Publishers, Articles, and Subscriptions.
"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser
    to handle role-based access.

    :param is_reader: Boolean indicating if the user is a Reader.
    :type is_reader: bool
    :param is_journalist: Boolean indicating if the user is a
        Journalist.
    :type is_journalist: bool
    :param is_editor: Boolean indicating if the user is an Editor.
    :type is_editor: bool
    :param subscribed_publishers: Many-to-many relationship with 
        Publisher model.
    :type subscribed_publishers: QuerySet
    :param subscribed_journalists: Many-to-many relationship with self
        for following Journalists.
    :type subscribed_journalists: QuerySet 
    """

    # Defining the roles
    is_reader = models.BooleanField(default=False)
    is_journalist = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)

    # Reader-specific data (subscribing to other users)
    subscribed_publishers = models.ManyToManyField(
        "Publisher", blank=True, related_name="subscribed_readers"
    )
    subscribed_journalists = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="journalist_subscribers",
    )

    def save(self, *args, **kwargs):
        """
        Ensure a user doesn't have Reader subscriptions
        if they are a Journalist or Editor.

        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        :return: None
        :rtype: None
        """
        if self.is_journalist or self.is_editor:
            if self.pk:  # If the user already exists
                self.subscribed_publishers.clear()
                self.subscribed_journalists.clear()
        super().save(*args, **kwargs)


class Publisher(models.Model):
    """
    Model representing a news publishing organization.

    :param name: Name of the publisher.
    :type name: str
    :param editors: Many-to-many relationship with
        User model for Editors.
    :type editors: QuerySet
    :param journalists: Many-to-many relationship with
        User model for Journalists.
    :type journalists: QuerySet
    """

    name = models.CharField(max_length=255)
    # Linking editors and journalists to a publisher
    editors = models.ManyToManyField(
        User,
        related_name="managed_publishers",
        limit_choices_to={"is_editor": True},
    )
    journalists = models.ManyToManyField(
        User,
        related_name="affiliated_publishers",
        limit_choices_to={"is_journalist": True},
    )

    def __str__(self):
        """
        Returns the string representation
        of the Publisher instance.

        :return: Name of the publisher.
        :rtype: str
        """
        return self.name


class Article(models.Model):
    """
    Model representing a news article or newsletter.

    :param content_type: Type of content (article or newsletter).
    :type content_type: str
    :param title: Title of the article.
    :type title: str
    :param content: Body of the article.
    :type content: str
    :param author: Foreign key to the User model for the author.
    :type author: User
    :param publisher: Foreign key to the Publisher model.
    :type publisher: Publisher
    :param published_at: Date and time when the article was published.
    :type published_at: datetime
    :param is_approved: Boolean indicating if the article
        is approved by an editor.
    :type is_approved: bool
    """

    CONTENT_TYPES = [
        ("article", "Article"),
        ("newsletter", "Newsletter"),
    ]
    content_type = models.CharField(
        max_length=20, choices=CONTENT_TYPES, default="article"
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_journalist": True},
        null=True,
        blank=True,
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        related_name="articles",
        null=True,
        blank=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    reader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="read_articles",
    )

    # Approval status managed by editors
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the string representation of the 
        Article instance.

        :return: Title of the article.
        :rtype: str
        """
        return self.title


class Subscription(models.Model):
    """
    Model representing a subscription of a reader to a
    publisher or journalist.

    :param user: Foreign key to the User model for the subscriber.
    :type user: User
    :param publisher: Foreign key to the Publisher model
        for the subscription.
    :type publisher: Publisher
    :param journalist: Foreign key to the User model for the
        journalist subscription.
    :type journalist: User
    :param created_at: Date and time when the subscription was created.
    :type created_at: datetime
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    publisher = models.ForeignKey(
        "Publisher", on_delete=models.CASCADE, null=True, blank=True
    )
    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscribers",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Enforces unique constraints for subscriptions.
        """

        # Ensure a user can't subscribe to the
        # same publisher or journalist multiple times
        unique_together = [
            ("user", "publisher"),
            ("user", "journalist")
        ]

    def __str__(self):
        """
        Returns the string representation of the Subscription instance.

        :return: String indicating the subscriber and the
            publisher or journalist they are subscribed to.
        :rtype: str
        """
        pub_name = self.publisher.name if self.publisher else "No Publisher"
        return f"{self.user.username} -> {pub_name}"
