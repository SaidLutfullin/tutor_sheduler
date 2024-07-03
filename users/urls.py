from django.urls import path

from users.views import LoginUser, logout_user, RegisterUser, MyProfileView

urlpatterns = [
    path("login", LoginUser.as_view(), name="login"),
    path("register", RegisterUser.as_view(), name="register"),
    path("logout", logout_user, name="logout"),
    path("my_profile", MyProfileView.as_view(), name="my_profile"),
]