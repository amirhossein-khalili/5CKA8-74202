from django.urls import path

from accounts.views import SignInView, SignUpView

app_name = "accounts"

urlpatterns = [
    path("signup", SignUpView.as_view(), name="signup"),
    path("signin", SignInView.as_view(), name="signin"),
]
