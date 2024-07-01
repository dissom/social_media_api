from django.urls import path, include
from rest_framework import routers
from social.views import (
    FollowUnfollowViewSet,
    PostViewSet,
    UserProfileView,
)


router = routers.DefaultRouter()
router.register("profiles", UserProfileView, basename="profile")
router.register('posts', PostViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "follow-unfollow/",
        FollowUnfollowViewSet.as_view(),
        name="follow_user"
    ),
]


app_name = "social"
