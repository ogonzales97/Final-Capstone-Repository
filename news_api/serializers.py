"""Serializer definitions for the news_api app."""
from rest_framework import serializers
from .models import Article, User, Publisher, Subscription


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    class Meta:
        """Meta class for UserSerializer."""
        model = User
        # Include relevant fields so API can identify user roles/types
        fields = [
            'id', 'username', 'email', 'is_reader',
            'is_journalist', 'is_editor'
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for the Publisher model."""
    class Meta:
        """Meta class for PublisherSerializer."""
        model = Publisher
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for the Article model.
    This will show an author's username instead of their ID."""
    author_name = serializers.ReadOnlyField(source='author.username')
    publisher_name = serializers.ReadOnlyField(source='publisher.name')

    class Meta:
        """Meta class for ArticleSerializer."""
        model = Article
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for handling subscription requests."""
    user = serializers.ReadOnlyField(source='user.username')
    publisher = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(), required=False, allow_null=True
    )
    journalist = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_journalist=True), required=False, allow_null=True
    )

    class Meta:
        """Meta class for SubscriptionSerializer."""
        model = Subscription
        fields = ['id', 'user', 'publisher', 'journalist']
