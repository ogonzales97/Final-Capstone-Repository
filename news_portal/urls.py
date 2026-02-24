"""
URL configuration for news_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from news_api import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"publishers", views.PublisherViewSet)
router.register(r"articles", views.ArticleViewSet)
router.register(
    r"subscriptions", views.SubscriptionViewSet, basename="subscription"
)

urlpatterns = [
    path(
        "admin/",
        (
            admin.site.view_config
            if hasattr(admin.site, "view_config")
            else admin.site.urls
        ),
    ),
    path("api/", include(router.urls)),
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
    path("", views.home_view, name="home"),
    path(
        "article/<int:pk>/", views.article_detail_view, name="article-detail"
    ),
    path("login/", views.login_view, name="custom_login"),
    path("logout/", views.logout_view, name="logout"),
    path("create/", views.create_article_view, name="create-article"),
    path("dashboard/", views.editor_dashboard_view, name="editor-dashboard"),
    path("my-feed/", views.my_feed_view, name="my-feed"),
    path("publishers/", views.publishers_list_view, name="publishers-list"),
    path(
        "edit-article/<int:pk>/", views.edit_article_view, name="edit-article"
    ),
    path("my-stories/", views.my_stories_view, name="my-stories"),
    path("signup/", views.signup_view, name="signup"),
    path("add-publisher/", views.add_publisher_view, name="add-publisher"),
]
