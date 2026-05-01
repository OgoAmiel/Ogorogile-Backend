from django.urls import path

from user_management.views import create_user, get_user, get_users, update_user

urlpatterns = [
    # Add URL patterns for user management here
    path("get_user/", get_user, name="get_user"),
    path("create_user/", create_user, name="create_user"),
    path("get_users/", get_users, name="get_users"),
    path("update_user/", update_user, name="update_user"),
]