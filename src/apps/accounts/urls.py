from django.urls import path
from .views import RegisterView, LoginView, RefreshView, LogoutView, MeView
from .views import WhoAmIView

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login",    LoginView.as_view()),
    path("refresh",  RefreshView.as_view()),
    path("logout",   LogoutView.as_view()),
    path("users/me", MeView.as_view()),
    path("whoami", WhoAmIView.as_view())
]

