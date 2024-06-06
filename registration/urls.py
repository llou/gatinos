from django.urls import path, include
from . import views

app_name = "registration"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("password_change/", views.PasswordChangeView.as_view(),
         name="password_change"),
    path("password_change_done/", views.PasswordChangeDoneView.as_view(),
         name="password_change_done"),
    ]
