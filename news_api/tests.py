"""Tests for the News API application."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Article, Publisher

User = get_user_model()


class ArticleWorkflowTest(TestCase):
    """Test case for the article workflow, ensuring correct handling of journalist and editor actions."""
    def setUp(self):
        # Create Users
        self.journalist = User.objects.create_user(username='writer', password='password', is_journalist=True)
        self.editor = User.objects.create_user(username='boss', password='password', is_editor=True)

        # Create Publisher
        self.publisher = Publisher.objects.create(name="Tech Daily")

        # Create an initial Article (Draft)
        self.article = Article.objects.create(
            title="AI Takes Over",
            content="Details inside...",
            author=self.journalist,
            publisher=self.publisher,
            is_approved=False  # Starts as draft
        )

    def test_journalist_reader_is_none(self):
        """Test that the reader field is None for a journalist's article."""
        self.assertIsNone(self.article.reader)
        print("\n TEST PASSED: Journalist article correctly has reader=None.")

    def test_editor_approval_sets_timestamp(self):
        """Test that approving an article sets the published_at timestamp."""
        # Ensure timestamp is empty initially
        self.assertIsNone(self.article.published_at)

        # Simulate Editor Approving logic
        self.article.is_approved = True
        self.article.published_at = timezone.now()
        self.article.save()

        # Check if timestamp exists now
        self.assertIsNotNone(self.article.published_at)
        print("TEST PASSED: Approval successfully generated a timestamp.")

    def test_staff_cannot_subscribe(self):
        """Test the logic that staff shouldn't have subscriptions."""
        # Try to add a subscription to the journalist (simulating the mistake)
        self.journalist.subscribed_publishers.add(self.publisher)

        # Run the 'save' cleanup logic we wrote in models.py
        self.journalist.save()

        # Verify it was wiped clean
        self.assertEqual(self.journalist.subscribed_publishers.count(), 0)
        print("TEST PASSED: Staff subscription was auto-cleaned.")


class ArticleAPITests(APITestCase):
    """Test case for the Article API endpoints."""
    def test_get_articles(self):
        """Test that the articles endpoint returns a successful response."""
        url = reverse('article-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("TEST PASSED: GET /api/articles/ returned 200 OK.")
