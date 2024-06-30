from django.db.models import Q
from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from social.models import UserProfile
from social.serializers import (
    FollowUnfollowSerializer,
    SocialLinkSerializer,
    UserProfileDetailSerializer,
    UserProfileListSerializerView,
    UserProfileSerializer,
)


class UserProfileView(viewsets.ModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        """Retrieve porfiles with filters by owner"""
        queryset = self.queryset.filter(
            Q(owner=self.request.user.id)
            | Q(followers=self.request.user.id)
            | Q(following=self.request.user.id)
        ).distinct()

        owner = self.request.query_params.get("owner")
        if owner:
            owner = owner.split(",")
            print(owner)
            queryset = queryset.filter(owner__username__in=owner)
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


class FollowUnfollowViewSet(APIView):
    serializer_class = FollowUnfollowSerializer

    def other_profile(self, pk):
        return get_object_or_404(UserProfile, id=pk)

    def post(self, request) -> Response:
        user_id = request.data.get("user_id")
        action = request.data.get("action")

        data = {"user_id": user_id, "action": action}
        serializer = FollowUnfollowSerializer(
            data=data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.data)
        return Response(
            {
                "message": f"Successfully {action}ed "
                f"{self.other_profile(user_id)}"
            },
            status=status.HTTP_200_OK
        )


class AddSocialLinkView(generics.UpdateAPIView):
    serializer_class = SocialLinkSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(owner=self.request.user)

    def put(self, request, *args, **kwargs):
        profile = get_object_or_404(
            UserProfile, owner=request.user
        )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_link = serializer.validated_data

        if profile.social_links:
            social_links = profile.social_links
        else:
            social_links = []

        social_links.append(new_link)
        profile.social_links = social_links
        profile.save()

        return Response(
            {"status": "social link added"},
            status=status.HTTP_200_OK
        )
