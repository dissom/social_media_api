from django.urls import path

from user.views import (
    CreateUserView,
    ManageUserView,
    LoginUserView,
    UserLogoutAPIView
)


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("manage/", ManageUserView.as_view(), name="manage"),
]


app_name = "user"
