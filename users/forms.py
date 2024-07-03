from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django import forms

from users.models import User


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={"class": "input my-2", "placeholder": "логин"}
        )
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"class": "input my-2", "placeholder": "пароль"}
        )
    )


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={"class": "input", "placeholder": "Логин"}
        ),
    )
    first_name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Имя"}),
    )
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"class": "input", "placeholder": "Пароль"}
        ),
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"class": "input", "placeholder": "Повторите пароль"}
        ),
    )

    class Meta(UserCreationForm):
        model = User
        fields = ("username", "first_name", "password1", "password2")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "username",
            "time_zone",
            "is_tutor"

        )
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "input my-1"}),
            "is_tutor": forms.CheckboxInput(attrs={"class": "form-control my-1"}),
            "time_zone": forms.Select(attrs={"class": "select my-1"}),
            "username": forms.TextInput(attrs={"class": "input my-1"}),
        }
        labels = {
            "first_name": "Имя",
            "time_zone": "Временная зона",
            "is_tutor": "Вы репетитор?",
            "username": "Логин"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрыть поле пароля
        self.fields['password'].widget = forms.HiddenInput()
        # Удалить помощь (help text) из поля пароля
        self.fields['password'].help_text = None