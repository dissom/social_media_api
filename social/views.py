from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404

from social.models import UserProfile
from social.serializers import (
    UserProfileDetailSerializer,
    UserProfileListSerializerView,
    UserProfileSerializer,
)


from user.models import User


class UserProfileView(viewsets.ModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(
            Q(owner=self.request.user.id) |
            Q(followers=self.request.user.id) |
            Q(following=self.request.user.id)
        ).distinct()

        owner = self.request.query_params.get("owner")
        if owner:
            owner = owner.split(",")
            print(owner)
            queryset = queryset.filter(
                owner__username__icontains=owner
            )
        return queryset

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "retrieve":
            serializer = UserProfileDetailSerializer
        if self.action == "list":
            serializer = UserProfileListSerializerView
        return serializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None) -> Response:
        """Endpoint for uploading image to User Profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def follow(request, pk) -> Response:

    owner = request.user
    user_to_follow = get_object_or_404(User, id=pk)
    if user_to_follow != owner:
        user_profile = get_object_or_404(
            UserProfile, owner=request.user
        )
        follow_profile = get_object_or_404(
            UserProfile, owner=user_to_follow
        )
        if user_profile.following.filter(id=follow_profile.id).exists():
            return Response(
                {"message": "Already following or invalid operation"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_profile.following.add(follow_profile)
        user_to_follow.profile.followers.add(user_profile)
        return Response(
            {"message": "Successfully followed"},
            status=status.HTTP_200_OK
        )

    return Response(
        {"message": "Invalid operation"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def unfollow(request, pk) -> Response:
    owner = request.user
    user_to_unfollow = get_object_or_404(User, id=pk)
    if user_to_unfollow != owner:
        user_profile = get_object_or_404(
            UserProfile, owner=owner
        )
        follow_profile = get_object_or_404(
            UserProfile, owner=user_to_unfollow
        )

        if user_profile.following.filter(id=follow_profile.id).exists():
            user_profile.following.remove(follow_profile)
            follow_profile.followers.remove(user_profile)
            return Response(
                {"message": "Successfully unfollowed"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": "Not following or invalid operation"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"message": "Invalid operation"}, status=status.HTTP_400_BAD_REQUEST
    )


# class FollowViewSet(APIView):
# queryset = UserProfile.objects.all()
# serializer_class = FollowUserSerializer

# def post(self, request, pk) -> Response:

#     owner = request.user
#     user_to_follow = get_object_or_404(User, id=pk)
#     if user_to_follow != owner:
#         user_profile = get_object_or_404(
#             UserProfile,
#             owner=request.user
#         )
#         follow_profile = get_object_or_404(
#             UserProfile,
#             owner=user_to_follow
#         )
#         if user_profile.following.filter(id=follow_profile.id).exists():
#             return Response(
#                 {"message": "Already following or invalid operation"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         user_profile.following.add(follow_profile)
#         user_to_follow.profile.followers.add(user_profile)
#         return Response(
#             {"message": "Successfully followed"}, status=status.HTTP_200_OK
#         )
#     # print(owner)
#     # print(user_to_follow)
#     return Response(
#         {"message": "Invalid operation"},
#         status=status.HTTP_400_BAD_REQUEST
#     )

# def delete(self, request, pk) -> Response:
#     owner = request.user
#     user_to_unfollow = get_object_or_404(User, id=pk)
#     if user_to_unfollow != owner:
#         user_profile = get_object_or_404(
#             UserProfile,
#             owner=request.user
#         )
#         follow_profile = get_object_or_404(
#             UserProfile,
#             owner=user_to_unfollow
#         )
#         if user_profile.following.filter(id=follow_profile.id).exists():
#             return Response(
#                 {"message": "Not following or invalid operation"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         user_profile.following.remove(user_to_unfollow)
#         user_to_unfollow.profile.followers.remove(user_profile)
#     # print(owner)
#     # print(user_to_follow)
#     return Response(status=status.HTTP_200_OK)
