from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import SignUpView, UserMeView


app_name = "users"


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", UserMeView.as_view(), name="user-me"),
]
