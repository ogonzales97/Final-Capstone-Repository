"""Views for the News API application."""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Article, Publisher, User, Subscription
from .serializers import (
    ArticleSerializer,
    PublisherSerializer,
    UserSerializer,
    SubscriptionSerializer,
)
from .permissions import IsJournalist, IsEditor, IsAuthorOrReadOnly
from .forms import SignUpForm


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.

    :param queryset: All users ordered by join date
    :type queryset: QuerySet
    :param serializer_class: Serializer for User data
    :type serializer_class: UserSerializer
    :param permission_classes: Required permissions for this view
    :type permission_classes: list
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class PublisherViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing publishers.

    :param queryset: All publishers
    :type queryset: QuerySet
    :param serializer_class: Serializer for Publisher data
    :type serializer_class: PublisherSerializer
    """
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing articles.

    :param queryset: All articles
    :type queryset: QuerySet
    :param serializer_class: Serializer for Article data
    :type serializer_class: ArticleSerializer
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """
        Assign permissions dynamically based on the action being taken.

        :param self: The instance of the ArticleViewSet
        :type self: ArticleViewSet
        :return: List of permission instances for the current action
        :rtype: list
        """
        if self.action == "create":
            # Only journalists can create articles
            permission_classes = [permissions.IsAuthenticated, IsJournalist]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Only the author editors can edit or delete articles
            permission_classes = [
                permissions.IsAuthenticated,
                IsAuthorOrReadOnly | IsEditor,
            ]
        else:
            # Everyone can view articles
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter the article queryset based on the user's role.

        :param self: The instance of the ArticleViewSet.
        :type self: ArticleViewSet
        :return: A filtered queryset of articles.
        :rtype: QuerySet
        """
        user = self.request.user
        if user.is_authenticated and (user.is_journalist or user.is_editor):
            return Article.objects.all()
        # Public/Readers only see approved content
        return Article.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        """
        Handles article creation logic, bypassing approval for
        independent journalists.

        :param self: The instance of the ArticleViewSet.
        :type self: ArticleViewSet
        :param serializer: The serializer instance containing the
            validated article data.
        :type serializer: ArticleSerializer
        :return: None
        :rtype: None
        """
        user = self.request.user
        publisher = serializer.validated_data.get("publisher", None)

        if user.is_journalist:
            if not publisher:
                # Independent bypass: Auto-approve and publish now
                # Also fulfills 'reader=None' requirement
                serializer.save(
                    author=user,
                    reader=None,
                    is_approved=True,
                    published_at=timezone.now(),
                )
            else:
                # Needs editor approval
                serializer.save(author=user, reader=None, is_approved=False)
        elif user.is_reader:
            # If a reader creates something, author is None or handled by model
            serializer.save(author=None, reader=user)
        else:
            # Fallback for editors or other staff
            serializer.save(author=user)

    def perform_update(self, serializer):
        """
        Set published_at timestamp when an editor approves an article
        and trigger email notifications.

        :param self: The instance of the ArticleViewSet.
        :type self: ArticleViewSet
        :param serializer: The serializer instance containing the
            validated update data.
        :type serializer: ArticleSerializer
        :return: None
        :rtype: None
        """
        # Check if 'is_approved' is being sent in the update data
        is_approved_data = self.request.data.get("is_approved")
        # Check if the article is being approved for the first time
        if is_approved_data is True and not serializer.instance.is_approved:
            # Save with the offical published timestamp
            # when an editor approves the article
            instance = serializer.save(
                published_at=timezone.now(), is_approved=True
            )

            # Notification logic to alert subscribers when an
            # article is approved
            subscribers = Subscription.objects.filter(
                Q(publisher=instance.publisher) |
                Q(journalist=instance.author)
            ).select_related("user")

            # Send real emails to all subscribers
            for sub in subscribers:
                subject = f"New Article Published: {instance.title}"
                message = f"""
Hello {sub.user.username},

A new article has been published that you might be interested in:

Title: {instance.title}
Author: {instance.author.username}
Publisher: {instance.publisher.name if instance.publisher else 'Independent'}

Read it here: http://127.0.0.1:8000/article/{instance.id}/

Best regards,
NewsPortal Team
                """

                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[sub.user.email],
                        fail_silently=False,
                    )
                    print(f"✓ Email sent to: {sub.user.email}")
                except Exception as e:
                    print(
                        f"Failed to send email to {sub.user.email}: {str(e)}"
                    )

        else:
            # For other updates, just save normally
            serializer.save()


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing reader subscriptions.

    :param serializer_class: The serializer used to parse
        Subscription data.
    :type serializer_class: SubscriptionSerializer
    :param permission_classes: The permissions required to
        access this view.
    :type permission_classes: list
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict the subscription queryset to the logged-in user.

        :param self: The instance of the SubscriptionViewSet.
        :type self: SubscriptionViewSet
        :return: A queryset of subscriptions belonging to the
            logged-in user.
        :rtype: QuerySet
        """
        # Return subscriptions for the logged-in user
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Handle subscription creation and prevent staff from
        subscribing.

        :param self: The instance of the SubscriptionViewSet.
        :type self: SubscriptionViewSet
        :param serializer: The serializer instance containing the
            validated subscription data.
        :type serializer: SubscriptionSerializer
        :raise PermissionDenied: If the user is a journalist or editor.
        :return: None
        :rtype: None
        """
        # If user is journalist/editor, they cannot subscribe to others
        if self.request.user.is_journalist or self.request.user.is_editor:
            raise PermissionDenied(
                "Staff members cannot subscribe to publishers."
            )
        serializer.save(user=self.request.user)


def home_view(request):
    """
    Render the homepage.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :return: The rendered homepage template.
    :rtype: django.http.HttpResponse
    """
    return render(request, "news_api/home.html")


def article_detail_view(request, pk):
    """
    Render the article detail page.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key (ID) of the article to display.
    :type pk: int
    :return: The rendered article detail template with the article
             ID in context.
    :rtype: django.http.HttpResponse
    """
    # Pass the 'pk' (article ID) to the template for client-side fetching
    context = {"article_id": pk}
    return render(request, "news_api/article_detail.html", context)


def login_view(request):
    """
    Handle user login via standard form submission.

    :param request: The incoming HTTP request containing
        login credentials.
    :type request: django.http.HttpRequest
    :return: Redirect to home on successful login or re-render
        the login page with an error message on failure.
    :rtype: django.http.HttpResponse
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(
                request,
                "news_api/login.html",
                {"error": "Invalid credentials"},
            )
    return render(request, "news_api/login.html")


def logout_view(request):
    """
    Handle user logout and clear session data.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :return: Redirect to the homepage after logging out.
    :rtype: django.http.HttpResponse
    """
    logout(request)
    return redirect("home")


def create_article_view(request):
    """
    Render the article creation page for journalists.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :return: The rendered article creation template.
    :rtype: django.http.HttpResponse
    """
    return render(request, "news_api/create_article.html")


def editor_dashboard_view(request):
    """
    Render the editor dashboard for managing articles.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :return: The rendered editor dashboard template or a redirect
        to the homepage if the user is not an editor.
    :rtype: django.http.HttpResponse
    """
    # Security check to ensure only editors can access this view
    if not request.user.is_authenticated or not request.user.is_editor:
        return redirect("home")
    return render(request, "news_api/editor_dashboard.html")


def my_feed_view(request):
    """
    Render the personalized feed for readers and clean up staff
    subscriptions.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :return: The rendered feed template or a redirect to login if
        the user is not authenticated.
    :rtype: django.http.HttpResponse
    """
    if not request.user.is_authenticated:
        return redirect("login")

        # If the user is a journalist or editor,
        # clear their subscriptions to avoid confusion
    if request.user.is_journalist or request.user.is_editor:
        Subscription.objects.filter(user=request.user).delete()
        return render(
            request,
            "news_api/my_feed.html",
            {"error_message": "Staff members do not have a personal feed."},
        )
    return render(request, "news_api/my_feed.html")


def publishers_list_view(request):
    """
    Render a list of publishers for readers to subscribe to.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :return: The rendered publishers list template.
    :rtype: django.http.HttpResponse
    """
    return render(request, "news_api/publishers_list.html")


def edit_article_view(request, pk):
    """
    Render the article editing page for journalists.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: The primary key (ID) of the article to edit.
    :type pk: int
    :return: The rendered article editing template with context.
    :rtype: django.http.HttpResponse
    """
    return render(request, "news_api/edit_article.html", {"pk": pk})


def my_stories_view(request):
    """
    Render a list of the journalist's own articles.

    :param request: The incoming HTTP request object.
    :type request: django.http.HttpRequest
    :return: The rendered my stories template.
    :rtype: django.http.HttpResponse
    """
    return render(request, "news_api/my_stories.html")


def signup_view(request):
    """
    Handle user registration with dynamic role selection.

    :param request: The incoming HTTP request object containing
        registration data.
    :type request: django.http.HttpRequest
    :return: Redirect to home on success, or the signup template
        on failure.
    :rtype: django.http.HttpResponse
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get("role")

            # Dynamically assign the role based on the dropdown selection
            user.is_reader = role == "reader"
            user.is_journalist = role == "journalist"
            user.is_editor = role == "editor"

            user.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "news_api/signup.html", {"form": form})


def add_publisher_view(request):
    """
    Render the page for editors to add new publishers.

    :param request: The incoming HTTP request object containing
        publisher data.
    :type request: django.http.HttpRequest
    :return: Redirect to editor dashboard on success, or the add
        publisher template on failure.
    :rtype: django.http.HttpResponse
    """
    # Security check to ensure only editors can access this view
    if not request.user.is_authenticated or not request.user.is_editor:
        return redirect("home")
    if request.method == "POST":
        name = request.POST.get("publisher_name")
        if name:
            Publisher.objects.create(name=name)
            messages.success(
                request, f'Publisher "{name}" added successfully!'
            )
            return redirect("editor-dashboard")
    return render(request, "news_api/add_publisher.html")
