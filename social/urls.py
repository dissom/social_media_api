from django.urls import path, include
from rest_framework import routers
from social.views import (
    UserProfileView,
    follow,
    unfollow,
)


router = routers.DefaultRouter()
router.register("profiles", UserProfileView, basename="profile")
print(router.urls)


urlpatterns = [
    path("", include(router.urls)),
    path("follow/<int:pk>/", follow, name="follow_user"),
    path("unfollow/<int:pk>/", unfollow, name="unfollow_user"),
]


app_name = "social"
