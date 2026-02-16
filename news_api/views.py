"""Views for the News API application."""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Article, Publisher, User, Subscription
from .serializers import ArticleSerializer, PublisherSerializer, UserSerializer, SubscriptionSerializer
from .permissions import IsJournalist, IsEditor, IsAuthorOrReadOnly
from .forms import SignUpForm


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class PublisherViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing publishers."""
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing articles."""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """Assign permissions based on action being taken."""
        if self.action == 'create':
            # Only journalists can create articles
            permission_classes = [permissions.IsAuthenticated, IsJournalist]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only the author editors can edit or delete articles
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly | IsEditor]
        else:
            # Everyone can view articles
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Readers only see approved articles; Authors see their own drafts."""
        user = self.request.user
        if user.is_authenticated and (user.is_journalist or user.is_editor):
            return Article.objects.all()
        # Public/Readers only see approved content
        return Article.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        """Handle the journalist 'None rule for the reader field."""
        if self.request.user.is_journalist:
            serializer.save(author=self.request.user, reader=None)
        else:
            serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Set published_at when an editor approves an article and trigger notifications."""
        # Check if 'is_approved' is being sent in the update data
        is_approved_data = self.request.data.get('is_approved')
        # Check if the article is being approved for the first time
        if is_approved_data is True and not serializer.instance.is_approved:
            # Save with the offical published timestamp when an editor approves the article
            instance = serializer.save(published_at=timezone.now(), is_approved=True)

            # Notification logic to alert subscribers when an article is approved
            print(f"\n--- NOTIFICATION LOGIC TRIGGERED FOR: {instance.title} ---")
            # Logic to find all relevant subscribers (both publisher and journalist)
            subscribers = Subscription.objects.filter(
                Q(publisher=instance.publisher) | Q(journalist=instance.author)
            ).select_related('user')

            # Simulate sending emails to all subscribers
            print(f"ACTION: Sending emails to {subscribers.count()} subscribers...")
            for sub in subscribers:
                print(f"   -> Email sent to: {sub.user.email} about new article: '{instance.title}'")

            # SImulate X/Twitter post since the X API free tier is very limited
            print("ACTION: Posting to X/Twitter via API...")
            print(f"   -> X Post: 'New article published: {instance.content_type}: {instance.title} by {instance.author.username} at {instance.publisher.name}'")
            print("--- NOTIFICATION LOGIC COMPLETED ---\n")

        else:
            # For other updates, just save normally
            serializer.save()


class SubscriptionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing reader subscriptions."""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Readers can only see their own subscriptions."""
        # Return subscriptions for the logged-in user
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Handle subscription creation logic."""
        # If user is journalist/editor, they cannot subscribe to others
        if self.request.user.is_journalist or self.request.user.is_editor:
            raise PermissionDenied("Staff members cannot subscribe to publishers.")
        serializer.save(user=self.request.user)


def home_view(request):
    """Render the homepage."""
    return render(request, 'news_api/home.html')


def article_detail_view(request, pk):
    """Render the article detail page."""
    # Pass the 'pk' (article ID) to the template for client-side fetching
    context = {'article_id': pk}
    return render(request, 'news_api/article_detail.html', context)


def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'news_api/login.html', {'error': 'Invalid credentials'})
    return render(request, 'news_api/login.html')


def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('home')


def create_article_view(request):
    """Render the article creation page for journalists."""
    return render(request, 'news_api/create_article.html')


def editor_dashboard_view(request):
    """Render the editor dashboard for managing articles."""
    # Security check to ensure only editors can access this view
    if not request.user.is_authenticated or not request.user.is_editor:
        return redirect('home')
    return render(request, 'news_api/editor_dashboard.html')


def my_feed_view(request):
    """Render the personalized feed for readers and clean up staff subscriptions."""
    if not request.user.is_authenticated:
        return redirect('login')

        # If the user is a journalist or editor, clear their subscriptions to avoid confusion
    if request.user.is_journalist or request.user.is_editor:
        Subscription.objects.filter(user=request.user).delete()
        return render(request, 'news_api/my_feed.html', {'error_message': 'Staff members do not have a personal feed.'})
    return render(request, 'news_api/my_feed.html')


def publishers_list_view(request):
    """Render a list of publishers for readers to subscribe to."""
    return render(request, 'news_api/publishers_list.html')


def edit_article_view(request, pk):
    """Render the article editing page for journalists."""
    return render(request, 'news_api/edit_article.html', {'pk': pk})


def my_stories_view(request):
    """Render a list of the journalist's own articles."""
    return render(request, 'news_api/my_stories.html')


def signup_view(request):
    """Handle reader-only registration."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Force new users to be readers only (no staff roles)
            user.is_reader = True
            user.is_journalist = False
            user.is_editor = False
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'news_api/signup.html', {'form': form})

