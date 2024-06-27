from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class LoginView(auth_views.LoginView):
    next_page = reverse_lazy("colonias")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_login"] = True
        return context


class LogoutView(auth_views.LogoutView):
    pass


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("registration:password_change_done")


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    pass
