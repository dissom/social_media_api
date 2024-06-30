from django.urls import path, include
from rest_framework import routers
from social.views import (
    AddSocialLinkView,
    FollowUnfollowViewSet,
    UserProfileView,
)


router = routers.DefaultRouter()
router.register("profiles", UserProfileView, basename="profile")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "follow-unfollow/",
        FollowUnfollowViewSet.as_view(),
        name="follow_user"
    ),
    path(
        "add-social-link/",
        AddSocialLinkView.as_view(),
        name="add-social-link"
    ),
]


app_name = "social"
