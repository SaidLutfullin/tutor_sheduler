from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import LoginUserForm, RegisterUserForm, CustomUserChangeForm
from users.mixins import LogoutRequiredMixin
from users.models import User


@login_required
def logout_user(request):
    logout(request)
    return redirect("login")


class LoginUser(LogoutRequiredMixin, LoginView):
    form_class = LoginUserForm
    template_name = "users/login.html"


class RegisterUser(LogoutRequiredMixin, CreateView):
    form_class = RegisterUserForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")


class MyProfileView(LoginRequiredMixin, UpdateView):
    form_class = CustomUserChangeForm
    template_name = "users/my_profile_edit.html"
    success_url = reverse_lazy("my_profile")

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.pk)