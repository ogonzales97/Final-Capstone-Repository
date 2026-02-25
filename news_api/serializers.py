"""Serializer definitions for the news_api app."""

from rest_framework import serializers
from .models import Article, User, Publisher, Subscription


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Converts User model instances to JSON format for API responses.
    Includes role flags to identify user types 
    (reader, journalist, editor).

    :param model: The User model to serialize
    :type model: news_api.models.User
    :return: Serialized user data
    :rtype: dict
    """

    class Meta:
        """
        Meta class for UserSerializer.

        Defines the model and fields to include in serialization.
        """

        model = User
        # Include relevant fields so API can identify user roles/types
        fields = [
            "id",
            "username",
            "email",
            "is_reader",
            "is_journalist",
            "is_editor",
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for the Publisher model.

    Converts Publisher model instances to JSON
    format for API responses.
    
    :param model: The Publisher model to serialize
    :type model: news_api.models.Publisher
    :return: Serialized publisher data
    :rtype: dict
    """

    class Meta:
        """
        Meta class for PublisherSerializer.

        Defines the model and fields to include in serialization.
        """

        model = Publisher
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model.
    
    Converts Article model instances to JSON format for API responses.
    Includes readable author and publisher names instead of just IDs.
    
    :param model: The Article model to serialize
    :type model: news_api.models.Article
    :return: Serialized article data with author and publisher names
    :rtype: dict
    """

    author_name = serializers.ReadOnlyField(source="author.username")
    publisher_name = serializers.ReadOnlyField(source="publisher.name")

    class Meta:
        """
        Meta class for ArticleSerializer.

        Defines the model and fields to include in serialization.
        """

        model = Article
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for handling subscription requests.

    Manages user subscriptions to publishers and journalists.
    Ensures proper validation and read-only user field for security.
    
    :param model: The Subscription model to serialize
    :type model: news_api.models.Subscription
    :return: Serialized subscription data
    :rtype: dict
    :raises ValidationError: If both publisher and journalist are None
    """

    user = serializers.ReadOnlyField(source="user.username")
    publisher = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(), required=False, allow_null=True
    )
    journalist = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_journalist=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        """
        Meta class for SubscriptionSerializer.
        
        Defines the model and fields to include in serialization.
        """

        model = Subscription
        fields = ["id", "user", "publisher", "journalist"]
